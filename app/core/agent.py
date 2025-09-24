import asyncio
from core.auxiliary import (
    fill_prompt_with_interview_v002,
    get_step_by_question_name,
    call_openai_responses,
    apply_fallback_if_needed,
)
from core.error_handling import check_data_is_not_empty
from core.asynchronous_call import openai_call, CallPlan, call_openai_responses_hedged
from io import BytesIO
from base64 import b64decode
from openai import OpenAI, AsyncOpenAI
import logging


class LLMAgent(object):
    """Class to manage LLM-based agents."""

    def __init__(self, openai_client: OpenAI):
        self.client = openai_client

    def load_parameters(self, parameters: dict):
        """Load interview guidelines for prompt construction."""
        self.parameters = parameters

    async def transcribe(self, audio) -> str:
        """Transcribe audio file."""
        logging.info("Starting transcription...")

        try:
            logging.info("Decoding base64 audio...")
            audio_bytes = b64decode(audio)
            logging.info(f"Decoded audio length: {len(audio_bytes)} bytes")

            audio_file = BytesIO(audio_bytes)
            audio_file.name = "audio.webm"
            logging.info(f"Audio file created with name: {audio_file.name}")

            logging.info("Sending audio to OpenAI Whisper API...")
            response = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="en",  # English language input
            )

            logging.info("Received response from Whisper API.")
            logging.info(f"Full response: {response}")

            return response.text
        except Exception as e:
            logging.error("Error occurred during transcription", exc_info=True)

    def execute_query_v002_auto(self, interview_manager):
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.execute_query_v002_async(interview_manager))
        else:
            return self.execute_query_v002_async(interview_manager)

    async def execute_query_v002_async(self, interview_manager) -> str:
        """
        Async entry point with hedged OpenAI call.
        """
        current_question = interview_manager.current_state["question_name"]

        step = get_step_by_question_name(
            parameters=interview_manager.parameters,
            question_name=current_question,
        )
        check_data_is_not_empty(data=step, name="Data for current question step")

        prompt = fill_prompt_with_interview_v002(
            step=step,
            global_prompt=interview_manager.parameters["global_mi_system_prompt"],
            history=interview_manager.history,
            history_indices=step.get("history_indices"),
            include_global_prompt=step.get("include_global_prompt", True),
        )

        text, full_response, plan, elapsed = await call_openai_responses_hedged(
            client=self.client,
            prompt=prompt,
            primary_model=step.get("model", "gpt-5-nano-2025-08-07"),
            fallback_model=step.get("fallback_model", "gpt-4o-mini"),
            hedge_delay_s=step.get("hedge_delay_s", 2.0),
            max_output_tokens=step.get("max_output_tokens", 200),
            reasoning_effort=step.get("reasoning_effort", "minimal"),
            per_request_timeout_s=step.get("per_request_timeout_s", 12.0),
        )

        interview_manager.set_open_ai_time(elapsed)

        answer = apply_fallback_if_needed(text=text, step=step)

        return answer
