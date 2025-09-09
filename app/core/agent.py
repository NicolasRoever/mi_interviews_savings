from asyncio import tasks
import logging
from core.auxiliary import (
    fill_prompt_with_interview_v002,
    get_step_by_question_name,
    call_openai_responses,
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

    def execute_query_v002(self, interview_manager) -> str:
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
            include_global_prompt=step.get("include_global_prompt", True),
        )

        text, full_response = call_openai_responses(
            client=self.client,
            prompt=prompt,
            model=step.get("model", "gpt-5-nano-2025-08-07"),
            max_output_tokens=step.get("max_output_tokens", 300),
            reasoning_effort=step.get("reasoning_effort", "minimal"),
        )

        logging.info(f"LLM full response: {full_response}")

        return text
