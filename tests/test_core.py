from app.core.auxiliary import chat_to_string_v002, get_step_by_question_name
import pytest
from decimal import Decimal
from app.parameters import INTERVIEW_PARAMETERS, GLOBAL_MI_SYSTEM_PROMPT


# ------------Test chat_to_string_v002 function -------------#


@pytest.fixture
def chat_history():
    return [
        {
            "summary": "",
            "topic_idx": Decimal("1"),
            "question_idx": Decimal("1"),
            "finish_idx": Decimal("1"),
            "question_name": "followup_past_positives",
            "session_id": "MI-TESTING-3521576",
            "time": Decimal("1757408482"),
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
            "session_id": "MI-TESTING-3521576",
            "time": Decimal("1757408485"),
            "type": "answer",
            "terminated": False,
            "content": "Currently, I am not saving money, because I am earning so little and prices are so high, that I just cant.",
            "order": Decimal("2"),
            "flagged_messages": Decimal("0"),
        },
        {
            "summary": "",
            "topic_idx": Decimal("1"),
            "question_idx": Decimal("1"),
            "finish_idx": Decimal("1"),
            "question_name": "followup_past_negatives",
            "session_id": "MI-TESTING-3521576",
            "time": Decimal("1757408495"),
            "type": "question",
            "terminated": False,
            "content": "It sounds like you’re currently facing financial pressure and not saving right now.\n\nEarlier you mentioned you’re not saving because income is low and prices are high. Thinking back, were there any times in the past when you managed to save even a small amount? What was different then?",
            "order": Decimal("3"),
            "flagged_messages": Decimal("0"),
        },
        {
            "summary": "",
            "topic_idx": Decimal("1"),
            "question_idx": Decimal("1"),
            "finish_idx": Decimal("1"),
            "question_name": "followup_past_negatives",
            "session_id": "MI-TESTING-3521576",
            "time": Decimal("1757408510"),
            "type": "answer",
            "terminated": False,
            "content": "Yeah, that was when I was meal-prepping, this really brought down my expenses.",
            "order": Decimal("4"),
            "flagged_messages": Decimal("0"),
        },
        {
            "summary": "",
            "topic_idx": Decimal("1"),
            "question_idx": Decimal("1"),
            "finish_idx": Decimal("1"),
            "question_name": "dig_deeper_past_experiences",
            "session_id": "MI-TESTING-3521576",
            "time": Decimal("1757408511"),
            "type": "question",
            "terminated": False,
            "content": "It sounds like meal-prepping helped you save in the past. thinking about times when saving didn’t happen, what negative experiences or obstacles tended to block your saving efforts?",
            "order": Decimal("5"),
            "flagged_messages": Decimal("0"),
        },
        {
            "summary": "",
            "topic_idx": Decimal("1"),
            "question_idx": Decimal("1"),
            "finish_idx": Decimal("1"),
            "question_name": "dig_deeper_past_experiences",
            "session_id": "MI-TESTING-3521576",
            "time": Decimal("1757408524"),
            "type": "answer",
            "terminated": False,
            "content": "When I get stressed, I just consume more to make me happy. Also, my past employer had an automatic retirement savings plan, which my current employer does not have.",
            "order": Decimal("6"),
            "flagged_messages": Decimal("0"),
        },
        {
            "summary": "",
            "topic_idx": Decimal("1"),
            "question_idx": Decimal("1"),
            "finish_idx": Decimal("1"),
            "question_name": "first_scaling_question",
            "session_id": "MI-TESTING-3521576",
            "time": Decimal("1757408526"),
            "type": "question",
            "terminated": False,
            "content": "You mentioned meal-prepping helped you save before — that seems like something that worked. Can you tell me more about that time: what exactly did you do with meal-prepping, and what kept you motivated to stick with it?",
            "order": Decimal("7"),
            "flagged_messages": Decimal("0"),
        },
        {
            "summary": "",
            "topic_idx": Decimal("1"),
            "question_idx": Decimal("1"),
            "finish_idx": Decimal("1"),
            "question_name": "first_scaling_question",
            "session_id": "MI-TESTING-3521576",
            "time": Decimal("1757408539"),
            "type": "answer",
            "terminated": False,
            "content": "That I had more time on my hand because the job wasn’t so demanding. I had more time to think about expenses.",
            "order": Decimal("8"),
            "flagged_messages": Decimal("0"),
        },
        {
            "summary": "",
            "topic_idx": Decimal("1"),
            "question_idx": Decimal("1"),
            "finish_idx": Decimal("1"),
            "question_name": "followup_first_scaling_question",
            "session_id": "MI-TESTING-3521576",
            "time": Decimal("1757408541"),
            "type": "question",
            "terminated": False,
            "content": "From what you’ve shared, meal-prepping helped you cut costs and save because you had more time and could plan expenses, while stress and lack of automatic saving options have made saving tougher. You’ve noted that income is tight and price levels are high, which makes saving hard right now, but you’ve also seen that when you had more control over time, you could focus on expenses and save a bit.\n\nOn a scale from 0 to 10, where 0 means 'not at all important' and 10 means 'extremely important', how important is it for you to save more money?",
            "order": Decimal("9"),
            "flagged_messages": Decimal("0"),
        },
        {
            "summary": "",
            "topic_idx": Decimal("1"),
            "question_idx": Decimal("1"),
            "finish_idx": Decimal("1"),
            "question_name": "followup_first_scaling_question",
            "session_id": "MI-TESTING-3521576",
            "time": Decimal("1757408592"),
            "type": "answer",
            "terminated": False,
            "content": "7",
            "order": Decimal("10"),
            "flagged_messages": Decimal("0"),
        },
        {
            "summary": "",
            "topic_idx": Decimal("1"),
            "question_idx": Decimal("1"),
            "finish_idx": Decimal("1"),
            "question_name": "dig_deeper_first_scaling_question",
            "session_id": "MI-TESTING-3521576",
            "time": Decimal("1757408595"),
            "type": "question",
            "terminated": False,
            "content": "Why is it a 7 and not a zero?",
            "order": Decimal("11"),
            "flagged_messages": Decimal("0"),
        },
        {
            "summary": "",
            "topic_idx": Decimal("1"),
            "question_idx": Decimal("1"),
            "finish_idx": Decimal("1"),
            "question_name": "dig_deeper_first_scaling_question",
            "session_id": "MI-TESTING-3521576",
            "time": Decimal("1757408607"),
            "type": "answer",
            "terminated": False,
            "content": "It is just that I need some backup money to cover emergency expenses like medical bills.",
            "order": Decimal("12"),
            "flagged_messages": Decimal("0"),
        },
        {
            "summary": "",
            "topic_idx": Decimal("1"),
            "question_idx": Decimal("1"),
            "finish_idx": Decimal("1"),
            "question_name": "imagine_benefits",
            "session_id": "MI-TESTING-3521576",
            "time": Decimal("1757408608"),
            "type": "question",
            "terminated": False,
            "content": "You mentioned having backup money for emergencies like medical bills. What is it about having that emergency fund that makes saving important to you right now?",
            "order": Decimal("13"),
            "flagged_messages": Decimal("0"),
        },
        {
            "summary": "",
            "topic_idx": Decimal("1"),
            "question_idx": Decimal("1"),
            "finish_idx": Decimal("1"),
            "question_name": "imagine_benefits",
            "session_id": "MI-TESTING-3521576",
            "time": Decimal("1757408621"),
            "type": "answer",
            "terminated": False,
            "content": "I just feel more secure so that I can sleep more soundly at night.",
            "order": Decimal("14"),
            "flagged_messages": Decimal("0"),
        },
        {
            "summary": "",
            "topic_idx": Decimal("1"),
            "question_idx": Decimal("1"),
            "finish_idx": Decimal("1"),
            "question_name": "second_scaling_question",
            "session_id": "MI-TESTING-3521576",
            "time": Decimal("1757408622"),
            "type": "question",
            "terminated": False,
            "content": "Thinking about what you’ve described, if you were able to save a bit more, what would that change for you day to day or in the bigger picture?",
            "order": Decimal("15"),
            "flagged_messages": Decimal("0"),
        },
        {
            "summary": "",
            "topic_idx": Decimal("1"),
            "question_idx": Decimal("1"),
            "finish_idx": Decimal("1"),
            "question_name": "second_scaling_question",
            "session_id": "MI-TESTING-3521576",
            "time": Decimal("1757408632"),
            "type": "answer",
            "terminated": False,
            "content": "I am also a more confident person - knowing you have your finances under control is a nice feeling.",
            "order": Decimal("16"),
            "flagged_messages": Decimal("0"),
        },
        {
            "summary": "",
            "topic_idx": Decimal("1"),
            "question_idx": Decimal("1"),
            "finish_idx": Decimal("1"),
            "question_name": "followup_second_scaling_question",
            "session_id": "MI-TESTING-3521576",
            "time": Decimal("1757408642"),
            "type": "question",
            "terminated": False,
            "content": "I hear that having a bit more security helps you sleep better and feel more confident overall. You’ve already identified benefits that saving more could bring to your daily life.\n\nOn a scale from 0 to 10, where 0 means 'not at all confident' and 10 means 'extremely confident', how confident are you that you could follow through if you decided to save more money?",
            "order": Decimal("17"),
            "flagged_messages": Decimal("0"),
        },
        {
            "summary": "",
            "topic_idx": Decimal("1"),
            "question_idx": Decimal("1"),
            "finish_idx": Decimal("1"),
            "question_name": "followup_second_scaling_question",
            "session_id": "MI-TESTING-3521576",
            "time": Decimal("1757408655"),
            "type": "answer",
            "terminated": False,
            "content": "7",
            "order": Decimal("18"),
            "flagged_messages": Decimal("0"),
        },
        {
            "summary": "",
            "topic_idx": Decimal("1"),
            "question_idx": Decimal("1"),
            "finish_idx": Decimal("1"),
            "question_name": "menu_of_choices_1",
            "session_id": "MI-TESTING-3521576",
            "time": Decimal("1757408657"),
            "type": "question",
            "terminated": False,
            "content": "Why is it a 7 and not a zero?",
            "order": Decimal("19"),
            "flagged_messages": Decimal("0"),
        },
        {
            "summary": "",
            "topic_idx": Decimal("1"),
            "question_idx": Decimal("1"),
            "finish_idx": Decimal("1"),
            "question_name": "menu_of_choices_1",
            "session_id": "MI-TESTING-3521576",
            "time": Decimal("1757408665"),
            "type": "answer",
            "terminated": False,
            "content": "I am usually a quite dedicated person. But with savings, there are just unexpected things happening, where I really cannot do anything.",
            "order": Decimal("20"),
            "flagged_messages": Decimal("0"),
        },
        {
            "summary": "",
            "topic_idx": Decimal("1"),
            "question_idx": Decimal("1"),
            "finish_idx": Decimal("1"),
            "question_name": "menu_of_choices_2",
            "session_id": "MI-TESTING-3521576",
            "time": Decimal("1757408667"),
            "type": "question",
            "terminated": False,
            "content": "You’ve already given some thoughtful reflections on what has helped before and what tends to derail saving. Thinking about next steps, what ideas do you have for saving more money, given your current situation? What small changes could you try first, and what would make them feel doable for you?",
            "order": Decimal("21"),
            "flagged_messages": Decimal("0"),
        },
        {
            "summary": "",
            "topic_idx": Decimal("1"),
            "question_idx": Decimal("1"),
            "finish_idx": Decimal("1"),
            "question_name": "menu_of_choices_2",
            "session_id": "MI-TESTING-3521576",
            "time": 1757408678,
            "type": "answer",
            "terminated": False,
            "content": "Have a second account where I am putting money automatically.",
            "order": Decimal("22"),
            "flagged_messages": Decimal("0"),
        },
    ]


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


def test_chat_to_string_v002_full_history(chat_history):
    chat = chat_history
    expected = (
        'Interviewer: "I am interested in your experiences on how you have been saving money. Could you tell me about your current savings habits?"\n'
        'Interviewee: "Currently, I am not saving money, because I am earning so little and prices are so high, that I just cant."\n'
        'Interviewer: "It sounds like you’re currently facing financial pressure and not saving right now.\n\nEarlier you mentioned you’re not saving because income is low and prices are high. Thinking back, were there any times in the past when you managed to save even a small amount? What was different then?"\n'
        'Interviewee: "Yeah, that was when I was meal-prepping, this really brought down my expenses."\n'
        'Interviewer: "It sounds like meal-prepping helped you save in the past. thinking about times when saving didn’t happen, what negative experiences or obstacles tended to block your saving efforts?"\n'
        'Interviewee: "When I get stressed, I just consume more to make me happy. Also, my past employer had an automatic retirement savings plan, which my current employer does not have."\n'
        'Interviewer: "You mentioned meal-prepping helped you save before — that seems like something that worked. Can you tell me more about that time: what exactly did you do with meal-prepping, and what kept you motivated to stick with it?"\n'
        'Interviewee: "That I had more time on my hand because the job wasn’t so demanding. I had more time to think about expenses."\n'
        "Interviewer: \"From what you’ve shared, meal-prepping helped you cut costs and save because you had more time and could plan expenses, while stress and lack of automatic saving options have made saving tougher. You’ve noted that income is tight and price levels are high, which makes saving hard right now, but you’ve also seen that when you had more control over time, you could focus on expenses and save a bit.\n\nOn a scale from 0 to 10, where 0 means 'not at all important' and 10 means 'extremely important', how important is it for you to save more money?\"\n"
        'Interviewee: "7"\n'
        'Interviewer: "Why is it a 7 and not a zero?"\n'
        'Interviewee: "It is just that I need some backup money to cover emergency expenses like medical bills."\n'
        'Interviewer: "You mentioned having backup money for emergencies like medical bills. What is it about having that emergency fund that makes saving important to you right now?"\n'
        'Interviewee: "I just feel more secure so that I can sleep more soundly at night."\n'
        'Interviewer: "Thinking about what you’ve described, if you were able to save a bit more, what would that change for you day to day or in the bigger picture?"\n'
        'Interviewee: "I am also a more confident person - knowing you have your finances under control is a nice feeling."\n'
        "Interviewer: \"I hear that having a bit more security helps you sleep better and feel more confident overall. You’ve already identified benefits that saving more could bring to your daily life.\n\nOn a scale from 0 to 10, where 0 means 'not at all confident' and 10 means 'extremely confident', how confident are you that you could follow through if you decided to save more money?\"\n"
        'Interviewee: "7"\n'
        'Interviewer: "Why is it a 7 and not a zero?"\n'
        'Interviewee: "I am usually a quite dedicated person. But with savings, there are just unexpected things happening, where I really cannot do anything."\n'
        'Interviewer: "You’ve already given some thoughtful reflections on what has helped before and what tends to derail saving. Thinking about next steps, what ideas do you have for saving more money, given your current situation? What small changes could you try first, and what would make them feel doable for you?"\n'
        'Interviewee: "Have a second account where I am putting money automatically."'
    )

    actual = chat_to_string_v002(chat)  # no indices → include full history
    assert actual == expected


def test_chat_to_string_v002_history_indices_7_8(chat_history):
    chat = chat_history

    expected = (
        'Interviewer: "You mentioned meal-prepping helped you save before — that seems like something that worked. '
        'Can you tell me more about that time: what exactly did you do with meal-prepping, and what kept you motivated to stick with it?"\n'
        'Interviewee: "That I had more time on my hand because the job wasn’t so demanding. I had more time to think about expenses."'
    )

    # history_indices filtering is based on `order`
    actual = chat_to_string_v002(chat, history_indices=[7, 8])
    assert actual == expected


# ------------Test get_step_by_question_name function -------------#


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
