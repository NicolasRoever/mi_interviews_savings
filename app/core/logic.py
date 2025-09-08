import logging
import os
from parameters import INTERVIEW_PARAMETERS, OPENAI_API_KEY
from core.manager import InterviewManager
from core.agent import LLMAgent
from database.dynamo import DynamoDB, connect_to_database
from typing import Union
from database.file import FileWriter


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

    interview_manager = InterviewManager(db=db, session_id=session_id)
    params = interview_parameters[interview_id]

    # Resume if interview has started, otherwise begin (new) session
    try:
        interview_manager.resume_session(parameters=params)

        interview = resume_interview_session(session_id, interview_id, user_message)
        parameters = interview.parameters
    except AssertionError:
        return begin_interview_session(session_id, interview_id)

    # Exit condition: this interview has been previously ended
    if interview.is_terminated():
        return {"session_id": session_id, "message": parameters["termination_message"]}

    # Provide interview guidelines to LLM agent
    agent.load_parameters(parameters)

    """
    UPDATE INTERVIEW WITH NEW USER MESSAGE
    Note this happens *after* security checks such that
    flagged messages are *not* added to interview history.
    """
    interview.add_chat_to_session(user_message, type="answer")

    ##### CONTINUE INTERVIEW BASED ON WORKFLOW #####

    # Current topic guide
    num_topics = len(parameters["interview_plan"])
    current_topic_idx = interview.get_current_topic()
    on_last_topic = current_topic_idx == num_topics
    current_question_name = interview.current_state.get("question_name", None)
    logging.info(f"On topic {current_topic_idx}/{num_topics}...")

    # Current question within topic guide
    current_question_idx = interview.get_current_topic_question()
    num_questions = parameters["interview_plan"][current_topic_idx - 1]["length"]
    on_last_question = current_question_idx >= num_questions
    logging.info(f"On question {current_question_idx}/{num_questions}...")

    next_question = agent.execute_query_v002(interview_manager=interview)

    # TODO: Add ending condition here

    interview.add_chat_to_session(next_question, type="question")

    return {"session_id": session_id, "message": next_question}


# ------------ Helper Functions -------------#


def resume_interview_session(
    session_id: str, interview_id: str, user_message: str
) -> InterviewManager:
    """Return InterviewManager object of existing session."""
    interview = InterviewManager(db, session_id)
    interview.resume_session(
        INTERVIEW_PARAMETERS[interview_id]
    )  # Why are you reinstating the class and overriding it?
    logging.info(
        "Generating next question for session '{}', user message '{}'".format(
            session_id, user_message
        )
    )
    return interview


def begin_interview_session(session_id: str, interview_id: str) -> dict:
    """Return response with starting question of new interview session."""
    if not INTERVIEW_PARAMETERS.get(interview_id):
        raise ValueError(f"Invalid interview parameters '{interview_id}' specified!")
    parameters = INTERVIEW_PARAMETERS[interview_id]
    interview = InterviewManager(db, session_id)
    interview.begin_session(parameters)
    message = parameters["first_question"]
    interview.add_chat_to_session(message, type="question")
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


# ------------ DB Helper Functions -------------#
# TODO SHould be a new database protocol class (or removed entirely because these are just one-liners....)


def load_interview_session(session_id: str) -> dict:
    """Return interview session history to user."""
    return db.load_remote_session(session_id)


def delete_interview_session(session_id: str):
    """Delete existing interview saved to database."""
    db.delete_remote_session(session_id)


def retrieve_sessions(db: Union[DynamoDB, FileWriter], sessions: list = None) -> dict:
    """Return specified or all existing interview sessions."""
    return db.retrieve_sessions(sessions)
