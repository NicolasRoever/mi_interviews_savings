from openai import OpenAI
import re
from typing import Optional, Tuple, Dict, Any
from agent.helper import _extract_content

# ---------- System Prompt (you can pass a different one per call) ----------
GENERAL_SYSTEM_PROMPT = (
    "You are a motivational interviewing counselor.\n"
    "- Use empathy and reflections (OARS).\n"
    "- Avoid advice or judgment.\n"
    "- Follow up with exactly the question: "
    "On a scale from 0 to 10, where 0 means 'not at all important' and 10 means 'extremely important', "
    "how important would you say it is for you to increase your savings?"
)

# ---------- Content validator (literal match; adjustable if you want variants) ----------
def contains_scaling_question(text: str) -> bool:
    """
    Checks for the presence of one of the key phrases in the scaling question.
    """
    pattern = (
        r"'extremely important'"
    )
    return bool(re.search(pattern, text, flags=re.IGNORECASE))

# ---------- One-shot OpenAI call (no inner defs) ----------
def openai_generate_mi_turn(
    *,
    client: OpenAI,
    model: str,
    system_prompt: str,
    user_message: str,
    verbose: bool = True,
):
    """
    Single Responses API call that returns a parsed JSON dict (thanks to schema).
    Prints the prompt (system + user) before sending if verbose=True.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    if verbose:
        print("\n--- OpenAI Request ---")
        print(f"Model: {model}")
        for m in messages:
            print(f"{m['role'].upper()}: {m['content']}")
        print("----------------------\n")

    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        reasoning_effort = "minimal"
    )

    print("\n--- OpenAI Response ---")
    print(resp)

    return resp # already a dict

# ---------- Main function you asked to adjust (stateless, no inner defs) ----------
def ask_scaling_question(
    client: OpenAI,
    user_message: str,
    *,
    model: str = "gpt-5-nano-2025-08-07",
    system_prompt: str,
) -> Tuple[str, Dict[str, Any]]:
    """
    Returns (utterance, metadata). No globals required.
    - Uses Structured Outputs with your simplified schema.
    - Validates that the literal scaling question is present (if require_literal_match=True).
    """
    # First attempt
    try:
        data = openai_generate_mi_turn(
            client=client,
            model=model,
            system_prompt=system_prompt,
            user_message=user_message,
        )
        if contains_scaling_question(_extract_content(data)):
            return _extract_content(data), data
    except Exception:
        pass  # fall through to retry/fallback

    # Deterministic fallback (always correct)
    return (
        "Ok."
        "On a scale from 0 to 10, where 0 means 'not at all important' and 10 means 'extremely important', "
        "how important would you say it is for you to increase your savings?"
    ), {"fallback": True}
