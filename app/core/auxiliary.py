from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import time
import logging
from typing import List, Dict, TypedDict, Iterable, Any, Optional
from decimal import Decimal
from datetime import datetime
import json
import logging
from typing import Any, Dict, Tuple
from openai import APIStatusError, APIConnectionError, AuthenticationError, OpenAI

Message = Dict[str, str]


def chat_to_string_v002(
    chat: List[Dict[str, Any]],
    only_topic: int = None,
    until_topic: int = None,
    question_orders: Optional[Iterable[int]] = None,  # NEW (optional)
) -> str:
    """Convert messages from chat into one string.
    If `question_orders` is provided, include ONLY those questions (by `order`)
    and their first following answers.
    """
    topic_history = ""
    # track whether the *next* answer should be emitted (only when its question matched)
    emit_next_answer = question_orders is None
    allowed_orders = (
        set(map(int, question_orders)) if question_orders is not None else None
    )

    for message in chat:
        # If desire specific topic's chat history:
        if only_topic and message["topic_idx"] != only_topic:
            continue
        if until_topic and message["topic_idx"] == until_topic:
            break

        if message["type"] == "question":
            # if filtering by question_orders, check this question's `order`
            if allowed_orders is not None:
                ord_val = message.get("order")
                if isinstance(ord_val, Decimal):
                    ord_val = int(ord_val)
                # decide whether to include this question (and its following answer)
                if ord_val in allowed_orders:
                    topic_history += f'Interviewer: "{message["content"]}"\n'
                    emit_next_answer = True
                else:
                    emit_next_answer = False
            else:
                topic_history += f'Interviewer: "{message["content"]}"\n'
                emit_next_answer = True

        if message["type"] == "answer":
            # only include the answer if we included the preceding question
            if emit_next_answer:
                topic_history += f'Interviewee: "{message["content"]}"\n'
                # reset so we only take the first following answer per question
                emit_next_answer = question_orders is None

    return topic_history.strip()


def fill_prompt_with_interview_v002(
    *,
    step: Dict[str, any],
    global_prompt: str,
    history: List[Message],
    history_indices: List[int] = None,
    include_global_prompt: bool = True,
) -> str:
    """
    Construct a prompt for OpenAI chat API:
    - Optionally start with the global/system prompt.
    - Insert interview history messages (user + assistant turns).
    - Append the current step's instructions as a system message.
    """
    logging.info("Filling prompt with interview v002...")
    logging.info(f"Step data is: {step}")
    logging.info(f"History indices are: {history_indices}")
    logging.info(f"History data is: {history}")
    if history_indices:
        history_for_prompt = chat_to_string_v002(
            history, question_orders=history_indices
        )
    else:
        history_for_prompt = chat_to_string_v002(history)

    logging.info(f"History for prompt is: {history_for_prompt}")

    prompt_parts = []
    if include_global_prompt:
        prompt_parts.append(global_prompt)
    prompt_parts.append(f"Interview History:\n{history_for_prompt}")
    prompt_parts.append(f"Instructions for next question:\n{step['system']}\n")

    prompt = "\n\n".join(prompt_parts)

    logging.info(f"Prompt to GPT:\n{prompt}")

    return prompt


def _preview(val: Any, limit: int = 600) -> str:
    if isinstance(val, str):
        return (val[:limit] + "…") if len(val) > limit else val
    try:
        s = json.dumps(val, ensure_ascii=False)
        return (s[:limit] + "…") if len(s) > limit else s
    except Exception:
        return f"<{type(val).__name__}>"


def get_step_by_question_name(
    parameters: Dict[str, Any], question_name: str
) -> Dict[str, Any]:
    """
    Given a *single interview* parameters dict (the one that contains 'interview_plan'),
    return the step dict whose 'question_name' matches. Raises KeyError if not found.
    """
    plan = parameters["interview_plan"]
    for step in plan:
        if step.get("question_name") == question_name:
            return step
    raise KeyError(f"question_name '{question_name}' not found")


def call_openai_responses(
    client: OpenAI,
    *,
    prompt: str,
    model: str = "gpt-4o-mini",
    max_output_tokens: int = 300,
    reasoning_effort: str = "minimal",
    log: logging.Logger | None = None,
) -> Tuple[str, Any]:
    """
    Calls the Responses API and returns (output_text, raw_response),
    while emitting detailed diagnostics for common failures.
    """
    log = log or logging.getLogger(__name__)
    log.info(
        "OpenAI request (Responses): model=%s max_output_tokens=%s reasoning_effort=%s",
        model,
        max_output_tokens,
        reasoning_effort,
    )
    log.debug("Prompt preview: %s", _preview(prompt))

    try:
        resp = client.responses.create(
            model=model,
            input=prompt,
            reasoning={"effort": reasoning_effort},
            max_output_tokens=max_output_tokens,
        )
        text = (getattr(resp, "output_text", None) or "").strip()
        log.info("OpenAI output_text present: %s", bool(text))
        log.debug("OpenAI raw response: %s", resp)
        return text, resp

    except APIStatusError as e:
        # 400s & friends: the JSON body tells you exactly what's wrong
        try:
            details = e.response.json()
        except Exception:
            details = getattr(e, "response", None)
        log.error("OpenAI APIStatusError %s: %s", e.status_code, details)
        raise
    except AuthenticationError as e:
        log.error("OpenAI AuthenticationError: %s", e)
        raise
    except APIConnectionError as e:
        log.error("OpenAI APIConnectionError: %s", e)
        raise
    except Exception as e:
        log.error("OpenAI unexpected error: %s", e)
        raise
