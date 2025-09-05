from helper import _render
import re




GLOBAL_MI_SYSTEM_PROMPT = (
    "You are a motivational interviewing counselor.\n"
    "- Use empathy and reflections (OARS).\n"
    "- Avoid advice or judgment.\n"
    "- One concise response per turn; end with ONE open question."
)


STEPS = [
    {
        "name": "followup_past_positives",
        "system": GLOBAL_MI_SYSTEM_PROMPT,
        "developer": (
            "Compose the next assistant message.\n"
            "Goal: Reflect what the user just said and turn attention to PAST POSITIVE SAVING EXPERIENCES.\n"
            "Requirements:\n"
            "- Start with a brief reflection (1 sentence).\n"
            "- Ask ONE open question about past times they saved successfully.\n"
            "- End with that question. ≤ 60 words."
        ),
        "on_user_reply": lambda reply, ctx: ctx.update({"past_successes": reply}),
        "next": lambda ctx: None,
    },
]
