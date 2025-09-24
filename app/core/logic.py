import logging
import os
from parameters import INTERVIEW_PARAMETERS, OPENAI_API_KEY
from core.manager import InterviewManager
from core.agent import LLMAgent
from database.dynamo import DynamoDB
from typing import Union
from database.file import FileWriter
import threading
import asyncio
from typing import Optional, Mapping, Any, Protocol, Callable, Dict, runtime_checkable
from pydantic import validate_arguments


# ------------ Main Interview Logic Function -------------#
def next_question(
    session_id: str,
    interview_id: str,
    db: Union[DynamoDB, FileWriter],
    agent: LLMAgent,
    interview_parameters: dict,
    user_message: str | None,
) -> dict:
    """
    Process user message and generate response by the AI-interviewer.

    Args:
        session_id: (str) unique interview session ID
        user_message: (str or None) interviewee response
        interview_id: (str) containing interview guidelines index
    Returns:
        response: (dict) containing `message` from interviewer
    """

    # Setup
    interview_manager = InterviewManager(db=db, session_id=session_id)
    params = interview_parameters[interview_id]
    agent.parameters = params

    # Check if we need to begin a new session
    maybe_payload = maybe_begin_session(
        session_id=session_id,
        interview_id=interview_id,
        db=db,
        agent=agent,
        interview_manager=interview_manager,
        parameters=params,
        begin_interview_session=begin_interview_session,
        warm_target=_warm_openai,  # your existing warmup function
    )
    if maybe_payload is not None:
        return maybe_payload

    else:
        interview_manager.resume_session(parameters=params)

    interview_manager.add_chat_to_session(
        message=user_message, type="answer"
    )  # TODO Here, type annotations are not super clear yet. The reason is that the flow structure is not so nice

    # Check if this was the last question
    if interview_manager.current_state["question_name"] == "last_question":
        return {"session_id": session_id, "message": params["termination_message"]}

    next_question = agent.execute_query_v002_auto(interview_manager=interview_manager)

    interview_manager.add_chat_to_session(message=next_question, type="question")
    interview_manager.update_parameters_after_question(
        question_name=interview_manager.current_state["question_name"]
    )

    return {"session_id": session_id, "message": next_question}


# ------------ Helper Functions -------------#


@validate_arguments
def maybe_begin_session(
    session_id: str,
    interview_id: str,
    db: Any,
    agent: Any,
    interview_manager: Any,
    parameters: Mapping[str, Any],
    begin_interview_session: Any,
    warm_target: Any,
) -> Dict[str, str] | None:
    """
    If no prior session exists, warm the agent asynchronously and start the interview.
    Otherwise, return None.

    Returns:
        dict with {"session_id": ..., "message": ...} when a new session begins, else None.
    """
    has_history = bool(db.load_remote_session(session_id))
    if has_history:
        return None

    threading.Thread(
        target=warm_target,
        kwargs={"agent": agent},
        daemon=True,
    ).start()

    return begin_interview_session(
        session_id=session_id,
        interview_id=interview_id,
        interview_manager=interview_manager,
        parameters=parameters,
    )


def begin_interview_session(
    session_id: str,
    interview_id: str,
    interview_manager: InterviewManager,
    parameters: dict,
) -> dict:
    """Return response with starting question of new interview session."""
    interview_manager.begin_session(parameters=parameters)
    message = parameters["first_question"]
    interview_manager.add_chat_to_session(message, type="question")
    logging.info(
        "Beginning {} interview session '{}' with prompt '{}'".format(
            interview_id, session_id, message
        )
    )
    return {"session_id": session_id, "interview_id": interview_id, "message": message}


def transcribe(audio: str, agent: LLMAgent) -> dict:
    """Return audio file transcription using OpenAI Whisper API"""
    logging.critical(f"Audio is: {type(audio)}...")
    transcription = agent.transcribe(audio)
    logging.info(f"Returning transcription text: '{transcription}'")
    return {"transcription": transcription}


def _warm_openai(agent: LLMAgent) -> None:
    """Warm the OpenAI client to hide cold-start latency."""
    logging.info("Warming OpenAI client...")
    try:
        manager = InterviewManager(db=None, session_id="warmup")
        manager.begin_session(
            parameters={
                "global_mi_system_prompt": "",
                "interview_plan": [
                    {
                        "question_name": "warmup",
                        "system": "Reply with a short acknowledgment.",
                        "model": "gpt-5-nano-2025-08-07",
                        "max_output_tokens": 20,
                    }
                ],
                "first_ai_question_name": "warmup",
            }
        )
        agent.execute_query_v002_auto(manager)
    except Exception:
        pass
