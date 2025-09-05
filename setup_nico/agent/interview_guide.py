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
        "on_user_reply": lambda reply, ctx: ctx.update({"followup_past_positives": reply}),
        "next": lambda ctx: "menu_of_choices_2",
    },
    {
        "name": "followup_past_negatives",
        "system": GLOBAL_MI_SYSTEM_PROMPT + (
            "Compose the next assistant message.\n"
            "Goal: Transition smoothly and ask ONE QUESTION about PAST NEGATIVE SAVING EXPERIENCES.\n"
        ),
        "on_user_reply": lambda reply, ctx: ctx.update({"past_failures": reply}),
        "next": lambda ctx: "dig_deeper_past_experiences",
    },
    {
        "name": "dig_deeper_past_experiences",
        "system": GLOBAL_MI_SYSTEM_PROMPT,
        "developer": (
            "Compose the next assistant message.\n"
            "Goal: Look at what the USER has said in 'Past Interview History' given above and ask a follow up into their past experiences saving money.\n"
            "------------------------------\n"
        ),
        "on_user_reply": lambda reply, ctx: ctx.update({"past_failures": reply}),
        "next": lambda ctx: "first_scaling_question",
    },
    {
        "name": "first_scaling_question",
        "system": GLOBAL_MI_SYSTEM_PROMPT,
        "developer": (
            "Compose the next assistant message.\n"
            "Goal: Summarize the past experiences the USER has shared in 'Past Interview History' in a concise manner.\n"
            "RESPONSE CONTRACT: Your response has to end with the exact question: \"On a scale from 0 to 10, where 0 means 'not at all important' and 10 means 'extremely important', how important is it for you to save more money?\""
        ),
        "on_user_reply": lambda reply, ctx: ctx.update({"past_failures": reply}),
        "next": lambda ctx: "followup_first_scaling_question",
        "validator": contains_scaling_question,
        "fallback": "Ok, so what would you say: On a scale from 0 to 10, where 0 means 'not at all important' and 10 means 'extremely important', how important is it for you to save more money?",
        "max_completion_tokens": 150,
    },

    {
        "name": "followup_first_scaling_question",
        "system": GLOBAL_MI_SYSTEM_PROMPT,
        "developer": (
            "Compose the next assistant message.\n"
            "RESPONSE CONTRACT: Ask exactly: \"Why is it a [insert user response from last question in past interview history'] and not a zero?\""
        ),
        "on_user_reply": lambda reply, ctx: ctx.update({"past_failures": reply}),
        "next": lambda ctx: "dig_deeper_first_scaling_question",
        "validator": correct_scaling_followup,
        "fallback": "And why is it not a zero?",
        "max_completion_tokens": 50,
    },
    {
        "name": "dig_deeper_first_scaling_question",
        "system": GLOBAL_MI_SYSTEM_PROMPT,
        "developer": (
            "Compose the next assistant message.\n"
            "Look at the past two answers and ask a follow up into the reasons why saving money is important to the user.\n"
            "RESPONSE CONTRACT: Your response has to end with a question."
        ),
        "on_user_reply": lambda reply, ctx: ctx.update({"dig_deeper_first_scaling_question": reply}),
        "next": lambda ctx: None,
        "max_completion_tokens": 100,
    },
    {
        "name": "imagine_benefits",
        "system": GLOBAL_MI_SYSTEM_PROMPT,
        "developer": (
            "Compose the next assistant message.\n"
            "Ask about what might change for the user if they were to save more money.\n"
            "RESPONSE CONTRACT: Your response has to end with a question."
        ),
        "on_user_reply": lambda reply, ctx: ctx.update({"imagine_benefits": reply}),
        "next": lambda ctx: "menu_of_choices_1",
        "max_completion_tokens": 100,
    }, 

    {
        "name": "menu_of_choices_1",
        "system": GLOBAL_MI_SYSTEM_PROMPT,
        "developer": (
            "Compose the next assistant message.\n"
            "Ask about what ideas the user has for saving more money.\n"
            "RESPONSE CONTRACT: Your response has to end with a question."
        ),
        "on_user_reply": lambda reply, ctx: ctx.update({"menu_of_choices": reply}),
        "next": lambda ctx: "menu_of_choices_2",
        "max_completion_tokens": 100,
    }, 


    {
        "name": "menu_of_choices_2",
        "system": GLOBAL_MI_SYSTEM_PROMPT,
        "developer": (
            "Compose the next assistant message.\n"
            "Follow-up on what the user has said in the last response(which you find in the 'Past Interview History' above) and encourage to come up with more ideas.\n"
            "RESPONSE CONTRACT: Your response has to end with a question."
        ),
        "on_user_reply": lambda reply, ctx: ctx.update({"menu_of_choices_2": reply}),
        "next": lambda ctx: "action_step",
        "max_completion_tokens": 100,
    }, 

    {
        "name": "action_step",
        "system": GLOBAL_MI_SYSTEM_PROMPT,
        "developer": (
            "Pull together key points and reinforce the participant's agency in a brief summary. Then ask about a small, but concrete action step that help the user to increase savings. \n"
            "RESPONSE CONTRACT: Your response has to end with a question."
        ),
        "on_user_reply": lambda reply, ctx: ctx.update({"menu_of_choices_2": reply}),
        "next": lambda ctx: None,
        "max_completion_tokens": 200,
    }, 



]
