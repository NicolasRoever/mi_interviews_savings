from typing import Dict, Any
import pytest
from agent.llm import contains_scaling_question

def test_contains_scaling_question_with_sample_response():
    # Hardcoded sample response (taken from your example)
    sample_response = (
        "That’s a thoughtful stance, and it sounds like you recognize its value. "
        "I’m glad you’re thinking about saving. On a scale from 0 to 10, "
        "where 0 means 'not at all important' and 10 means 'extremely important', "
        "how important would you say it is for you to increase your savings?"
    )

    # Run the function
    result = contains_scaling_question(sample_response)

    # Assert it detects the phrase
    assert result is True