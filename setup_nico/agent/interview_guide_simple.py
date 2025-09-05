from helper import _render
from llm import contains_scaling_question, correct_scaling_followup
import re




GLOBAL_MI_SYSTEM_PROMPT = (
    "You are a motivational interviewing counselor.\n"
    "- Use empathy and reflections (OARS).\n"
    "- Ask only ONE question per response."
)

STEPS = [
    {
        "name": "followup_past_positives",
        "system": GLOBAL_MI_SYSTEM_PROMPT + (
            "Compose the next assistant message.\n"
            "Reflect what the user just said (relying on the past interview history above) and turn attention to PAST POSITIVE SAVING EXPERIENCES.\n"
            "RESPONSE CONTRACT: Your response has to end with a question.\n"
        ),

    },
    {
        "name": "followup_past_negatives",
        "system": GLOBAL_MI_SYSTEM_PROMPT + (
            "Compose the next assistant message.\n"
            "Goal: Transition smoothly and ask ONE QUESTION about PAST NEGATIVE SAVING EXPERIENCES.\n"
        ),
    },
    {
        "name": "dig_deeper_past_experiences",
        "system": GLOBAL_MI_SYSTEM_PROMPT,
        "developer": (
            "Compose the next assistant message.\n"
            "Goal: Look at what the user has said in 'Past Interview History' given above and ask a follow up into their past experiences saving money.\n"
            "------------------------------\n"
        )
    }
]