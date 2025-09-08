from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import time
import logging
from typing import List, Dict, TypedDict, Iterable, Any, Optional
from decimal import Decimal
from datetime import datetime

Message = Dict[str, str]


def chat_to_string(chat: list, only_topic: int = None, until_topic: int = None) -> str:
    """Convert messages from chat into one string."""
    topic_history = ""
    for message in chat:
        # If desire specific topic's chat history:
        if only_topic and message["topic_idx"] != only_topic:
            continue
        if until_topic and message["topic_idx"] == until_topic:
            break
        if message["type"] == "question":
            topic_history += f"Interviewer: '{message['content']}'\n"
        if message["type"] == "answer":
            topic_history += f"Interviewee: '{message['content']}'\n"
    return topic_history.strip()


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
) -> str:
    """
    Construct a prompt for OpenAI chat API:
    - Start with the global/system prompt.
    - Insert interview history messages (user + assistant turns).
    - Append the current step's instructions as a system message.
    """
    logging.info("Filling prompt with interview v002...")
    logging.info(f"Step data is: {step}")
    logging.info(f"History indices are: {history_indices}")
    logging.info(f"History data is: {history}")
    if history_indices is None:
        history_for_prompt = chat_to_string_v002(
            history, question_orders=history_indices
        )
    else:
        history_for_prompt = chat_to_string_v002(history)

    logging.info(f"History for prompt is: {history_for_prompt}")

    # Build a string with the current interview state and history
    prompt = (
        f"{global_prompt}\n\n"
        f"Interview History:\n{history_for_prompt}\n\n"
        f"Instructions for next question:\n{step['system']}\n"
    )
    logging.info(f"Prompt to GPT:\n{prompt}")

    return prompt


def fill_prompt_with_interview(
    template: str, topics: list, history: list, user_message: str = None
) -> str:
    """Fill the prompt template with parameters from current interview."""
    state = history[-1]
    current_topic_idx = min(int(state["topic_idx"]), len(topics))
    next_topic_idx = min(current_topic_idx + 1, len(topics))
    current_topic_chat = chat_to_string(history, only_topic=current_topic_idx)
    prompt = template.format(
        topics="\n".join([topic["topic"] for topic in topics]),
        question=state["content"],
        answer=user_message,
        summary=state["summary"]
        or chat_to_string(history, until_topic=current_topic_idx),
        current_topic=topics[current_topic_idx - 1]["topic"],
        next_interview_topic=topics[next_topic_idx - 1]["topic"],
        current_topic_history=current_topic_chat,
    )
    logging.info(f"Prompt to GPT:\n{prompt}")
    assert not re.findall(r"\{[^{}]+\}", prompt)
    return prompt


def execute_queries(query, task_args: dict) -> dict:
    """
    Execute queries (concurrently if multiple).

    Args:
        query: function to execute
        task_args: (dict) of arguments for each task's query
    Returns:
        suggestions (dict): {task: output}
    """
    st = time.time()
    suggestions = {}
    with ThreadPoolExecutor(max_workers=len(task_args)) as executor:
        futures = {
            executor.submit(query, **kwargs): task for task, kwargs in task_args.items()
        }
        for future in as_completed(futures):
            task = futures[future]
            resp = future.result().choices[0].message.content.strip("\n\" '''")
            suggestions[task] = resp

    logging.info("OpenAI query took {:.2f} seconds".format(time.time() - st))
    logging.info(f"OpenAI query returned: {suggestions}")
    return suggestions


def _extract_content(response: dict) -> str:
    """Extract content from OpenAI response."""
    return response["choices"][0]["message"]["content"].strip("\n\" '''")


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
