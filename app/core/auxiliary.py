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
from openai import (
    APIStatusError,
    APIConnectionError,
    AuthenticationError,
    OpenAI,
    AsyncOpenAI,
)
from dataclasses import dataclass
from core.error_handling import handle_openai_error, check_data_is_not_empty
import asyncio
import logging

Message = Dict[str, str]


def chat_to_string_v002(
    chat: List[Dict[str, Any]],
    history_indices: Optional[Iterable[int]] = None,
) -> str:
    """
    Render chat history as lines like:
      Interviewer: "..."
      Interviewee: "..."

    - If `history_indices` is None, include the whole history.
    - If `history_indices` is provided, include only messages whose `order`
      (int) is in that list.
    - Negative indices are interpreted relative to the end of the chat
      (like Python list indexing).
    """
    if not chat:
        return ""

    # Precompute list of available order values in sequence
    orders: List[int] = []
    for msg in chat:
        ord_val = msg.get("order")
        if isinstance(ord_val, Decimal):
            ord_val = int(ord_val)
        elif isinstance(ord_val, (int, float, str)) and ord_val is not None:
            ord_val = int(ord_val)
        else:
            ord_val = None
        orders.append(ord_val)

    allowed: Optional[set[int]] = None
    if history_indices is not None:
        resolved = []
        n = len(chat)
        for idx in history_indices:
            if idx < 0:  # negative index: count from end
                pos = n + idx  # e.g. -1 -> n-1
                if 0 <= pos < n:
                    if orders[pos] is not None:
                        resolved.append(orders[pos])
            else:
                resolved.append(int(idx))
        allowed = set(resolved)

    lines: List[str] = []
    for i, msg in enumerate(chat):
        ord_val = orders[i]
        if allowed is not None:
            if ord_val is None or ord_val not in allowed:
                continue

        role = msg.get("type")
        content = msg.get("content", "")
        if role == "question":
            lines.append(f'Interviewer: "{content}"')
        elif role == "answer":
            lines.append(f'Interviewee: "{content}"')
        # ignore other types silently

    return "\n".join(lines).strip()


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
    logging.info(f"Step data is: {step}")
    logging.info(f"History data is: {history}")
    if history_indices:
        history_for_prompt = chat_to_string_v002(
            history, history_indices=history_indices
        )
    else:
        history_for_prompt = chat_to_string_v002(history)

    prompt_parts = []
    if include_global_prompt:
        prompt_parts.append(global_prompt)
    prompt_parts.append(f"Interview History:\n{history_for_prompt}")
    prompt_parts.append(f"Instructions for next question:\n{step['system']}\n")

    prompt = "\n\n".join(prompt_parts)

    logging.info(f"Prompt to GPT:\n{prompt}")

    return prompt


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
    max_output_tokens: int = 200,
    reasoning_effort: str = "minimal",
) -> Tuple[str, Any]:
    """
    Calls the Responses API and returns (output_text, raw_response),
    while emitting detailed diagnostics for common failures.
    """
    logging.debug("Prompt preview: %s", _preview(prompt))

    try:
        start = time.perf_counter()
        resp = client.responses.create(
            model=model,
            input=prompt,
            reasoning={"effort": reasoning_effort},
            max_output_tokens=max_output_tokens,
        )
        text = (getattr(resp, "output_text", None) or "").strip()
        elapsed = time.perf_counter() - start
        logging.info("OpenAI call completed in %.3f seconds", elapsed)
        logging.debug("OpenAI raw response: %s", resp)
        return text, resp

    except Exception as e:
        handle_openai_error(e)


def _preview(val: Any, limit: int = 600) -> str:
    if isinstance(val, str):
        return (val[:limit] + "…") if len(val) > limit else val
    try:
        s = json.dumps(val, ensure_ascii=False)
        return (s[:limit] + "…") if len(s) > limit else s
    except Exception:
        return f"<{type(val).__name__}>"
