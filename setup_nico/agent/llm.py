from openai import OpenAI
import re
from typing import Optional, Tuple, Dict, Any, Callable, List
from helper import _extract_content, _render


# ---- tiny engine (no validators, no LLM) ----

def run_flow(
    *,
    client: OpenAI,
    steps: List[Dict[str, Any]],
    get_user_reply: Callable[[str], str],
    ctx: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    ctx = ctx or {}
    ctx.setdefault("history", [])

    # --- Step 1: hardcoded opening ---
    q1 = (
        "I’m interested in your experiences with saving money. "
        "Could you tell me about your current savings habits?"
    )
    print(f"\nASSISTANT: {q1}")
    ctx["history"].append({"role": "assistant", "content": q1})
    u1 = get_user_reply(q1)
    ctx["history"].append({"role": "user", "content": u1})
    ctx["savings_habits"] = u1

    # --- Next steps: use LLM engine ---
    names = [s["name"] for s in steps]
    idx = 0
    while idx is not None:
        step = steps[idx]
        assistant_text = llm_step(
            client=client,
            model=step.get("model", "gpt-5-nano-2025-08-07"),
            step=step,
            ctx=ctx,
        )
        print(f"\nASSISTANT: {assistant_text}")
        ctx["history"].append({"role": "assistant", "content": assistant_text})

        user_text = get_user_reply(assistant_text)
        ctx["history"].append({"role": "user", "content": user_text})

        if "on_user_reply" in step and step["on_user_reply"]:
            step["on_user_reply"](user_text, ctx)

        nxt = step.get("next", lambda _ctx: None)(ctx)
        idx = names.index(nxt) if nxt else None

    return ctx

# ---- demo I/O ----
def get_user_reply_cli(_prompt_to_user: str) -> str:
    return input("YOU: ")













#--------LLM Step---------#

def llm_step(
    *,
    client: OpenAI,
    model: str,
    step: Dict[str, Any],
    ctx: Dict[str, Any],
    verbose: bool = True,
) -> str:
    """
    Reusable function: builds messages from the step spec (system+developer) + history,
    calls the old chat.completions API, and returns the assistant's text.
    """
    system_txt = _render(step.get("system", ""), ctx)
    dev_txt    = _render(step.get("developer", ""), ctx)

    messages = [
        {'role': 'system', 'content': f"Past Interview History: \n {ctx.get('history', '')} \n------------------------------"}
    ]
    if system_txt:
        messages.append({"role": "system", "content": system_txt})
    if dev_txt:
        messages.append({"role": "developer", "content": dev_txt})

    if verbose:
        print("\n--- OpenAI Request ---")
        for m in messages:
            print(f"{m['role'].upper()}: {m['content']}")
        print("----------------------")

    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        reasoning_effort="minimal",
        max_completion_tokens=step.get("max_completion_tokens", 300)
    )
    draft = _extract_content(resp)

    print("\n--- OpenAI Response ---")
    print(resp)


    #Validate Question if validator present
    validator = step.get("validator")
    if callable(validator) and not validator(draft):
        fallback = step.get("fallback") or ""
        ctx.setdefault("flags", {})[f"{step['name']}_fallback_used"] = True
        return fallback.strip()

    return draft.strip()















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

def correct_scaling_followup(text: str) -> bool:
    """
    Checks for the presence of one of the key phrases in the scaling question.
    """
    pattern = (
        r"Why is it a "
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
