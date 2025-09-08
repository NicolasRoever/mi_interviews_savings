from asyncio import tasks
import logging
from core.auxiliary import (
    execute_queries,
    fill_prompt_with_interview,
    chat_to_string,
    fill_prompt_with_interview_v002,
    chat_to_string_v002,
    _extract_content,
    get_step_by_question_name,
)
from core.error_handling import check_data_is_not_empty
from io import BytesIO
from base64 import b64decode
from openai import OpenAI


class LLMAgent(object):
    """Class to manage LLM-based agents."""

    def __init__(self, openai_client: OpenAI):
        self.client = openai_client

    def load_parameters(self, parameters: dict):
        """Load interview guidelines for prompt construction."""
        self.parameters = parameters

    def transcribe(self, audio) -> str:
        """Transcribe audio file."""
        audio_file = BytesIO(b64decode(audio))
        audio_file.name = "audio.webm"

        response = self.client.audio.transcriptions.create(
            model="whisper-1", file=audio_file, language="en"  # English language input
        )
        return response.text

    def execute_query_v002(self, interview_manager) -> dict:
        """
        We simply need a function analogous to llm_step in my setup. This constructs the prompt using the information stored in the interview manager class.
        """
        logging.info("Executing query v002...")
        current_question = interview_manager.current_state["question_name"]
        logging.info(f"Current question is: {current_question}")

        step = get_step_by_question_name(
            parameters=interview_manager.parameters, question_name=current_question
        )
        check_data_is_not_empty(data=step, name="Data for current question step")

        logging.info(f"Step data retrieved is: {step}")
        logging.info(f"History is: {interview_manager.history}")

        prompt = fill_prompt_with_interview_v002(
            step=step,
            global_prompt=interview_manager.parameters["global_mi_system_prompt"],
            history=interview_manager.history,
            history_indices=step.get("history_indices", None),
        )

        response = self.client.chat.completions.create(
            messages=prompt,
            model=step.get("model", "gpt-4o-mini"),
            reasoning_effort=step.get("reasoning_effort", "minimal"),
            max_completion_tokens=step.get("max_completion_tokens", 300),
        )

        return _extract_content(response)

    # ------------Deprecated Functions-------------#

    def review_answer(self, message: str, history: list) -> bool:
        """Moderate answers: Are they on topic?"""
        response = execute_queries(
            self.client.chat.completions.create,
            self.construct_query(["moderator"], history, message),
        )
        return "yes" in response["moderator"].lower()

    def review_question(self, next_question: str) -> bool:
        """Moderate questions: Are they flagged by the moderation endpoint?"""
        response = self.client.moderations.create(
            model="omni-moderation-latest",
            input=next_question,
        )
        return response.to_dict()["results"][0]["flagged"]

    def probe_within_topic(self, history: list) -> str:
        """Return next 'within-topic' probing question."""
        response = execute_queries(
            self.client.chat.completions.create,
            self.construct_query(["probe"], history),
        )
        return response["probe"]

    def transition_topic(self, history: list) -> tuple[str, str]:
        """
        Determine next interview question transition from one topic
        cluster to the next. If have defined `summarize` model in parameters
        will also get summarization of interview thus far.
        """
        summarize = self.parameters.get("summarize")
        tasks = ["summary", "transition"] if summarize else ["transition"]
        response = execute_queries(
            self.client.chat.completions.create, self.construct_query(tasks, history)
        )
        return response["transition"], response.get("summary", "")

    def construct_query(
        self, tasks: list, history: list, user_message: str = None
    ) -> dict:
        """
        Construct OpenAI API completions query,
        defaults to `gpt-4o-mini` model, 300 token answer limit, and temperature of 0.
        For details see https://platform.openai.com/docs/api-reference/completions.
        """

        query_dict = {}
        for task in tasks:
            model = self.parameters[task].get("model", "gpt-4o-mini")
            base_dict = {
                "messages": [
                    {
                        "role": "user",
                        "content": fill_prompt_with_interview(
                            self.parameters[task]["prompt"],
                            self.parameters["interview_plan"],
                            history,
                            user_message=user_message,
                        ),
                    }
                ],
                "model": model,
            }

            # Add "max_tokens" and "temperature" if model contains "4"
            if "4" in model:
                base_dict["max_tokens"] = self.parameters[task].get("max_tokens", 300)
                base_dict["temperature"] = self.parameters[task].get("temperature", 0)
            else:
                # If no "4" in model, add "max_completion_tokens" only, no temperature
                base_dict["max_completion_tokens"] = self.parameters[task].get(
                    "max_completion_tokens", 300
                )

            query_dict[task] = base_dict

        return query_dict
