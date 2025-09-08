from app.core.auxiliary import chat_to_string_v002, get_step_by_question_name
import pytest
from decimal import Decimal
from app.parameters import INTERVIEW_PARAMETERS, GLOBAL_MI_SYSTEM_PROMPT


def test_chat_to_string_v002_basic_pair():
    chat = [
        {
            "summary": "",
            "topic_idx": Decimal("1"),
            "question_idx": Decimal("1"),
            "finish_idx": Decimal("1"),
            "question_name": "followup_past_positives",
            "session_id": "MI-TESTING-49637760",
            "time": Decimal("1757329351"),
            "type": "question",
            "terminated": False,
            "content": "I am interested in your experiences on how you have been saving money. Could you tell me about your current savings habits?",
            "order": Decimal("1"),
            "flagged_messages": Decimal("0"),
        },
        {
            "summary": "",
            "topic_idx": Decimal("1"),
            "question_idx": Decimal("1"),
            "finish_idx": Decimal("1"),
            "question_name": "followup_past_positives",
            "session_id": "MI-TESTING-49637760",
            "time": 1757329359,
            "type": "answer",
            "terminated": False,
            "content": "Not really keeping track right now.",
            "order": Decimal("2"),
            "flagged_messages": Decimal("0"),
        },
    ]

    expected = (
        'Interviewer: "I am interested in your experiences on how you have been saving money. '
        'Could you tell me about your current savings habits?"\n'
        'Interviewee: "Not really keeping track right now."'
    )

    actual = chat_to_string_v002(chat)
    assert actual == expected


def test_get_step_by_question_name_first_step():
    params = {
        "_name": "MI_FINANCE",
        "_description": "Motivational interview.",
        "first_question": "I am interested in your experiences on how you have been saving money. Could you tell me about your current savings habits?",
        "first_ai_question_name": "followup_past_positives",
        "interview_plan": [
            {
                "question_name": "followup_past_positives",
                "system": (
                    "Compose the next assistant message.\n"
                    "Reflect what the user just said (relying on the past interview history above) and turn attention to PAST POSITIVE SAVING EXPERIENCES.\n"
                    "RESPONSE CONTRACT: Your response has to end with a question.\n"
                ),
            },
            {
                "question_name": "followup_past_negatives",
                "system": (
                    "Compose the next assistant message.\n"
                    "Goal: Transition smoothly and ask ONE QUESTION about PAST NEGATIVE SAVING EXPERIENCES.\n"
                ),
            },
            {
                "question_name": "dig_deeper_past_experiences",
                "system": "You are a motivational interviewing counselor.\n- Use empathy and reflections (OARS).\n- Ask only ONE question per response.",
                "developer": (
                    "Compose the next assistant message.\n"
                    "Goal: Look at what the user has said in 'Past Interview History' given above and ask a follow up into their past experiences saving money.\n"
                    "------------------------------\n"
                ),
            },
        ],
    }

    expected = {
        "question_name": "followup_past_positives",
        "system": (
            "Compose the next assistant message.\n"
            "Reflect what the user just said (relying on the past interview history above) and turn attention to PAST POSITIVE SAVING EXPERIENCES.\n"
            "RESPONSE CONTRACT: Your response has to end with a question.\n"
        ),
    }

    out = get_step_by_question_name(params, "followup_past_positives")
    assert out == expected
