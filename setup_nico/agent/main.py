from openai import OpenAI
from config import OPENAI_API_KEY
from llm import ask_scaling_question, GENERAL_SYSTEM_PROMPT, openai_generate_mi_turn
from typing import Dict, Any, Optional, Tuple

def main(api_key=OPENAI_API_KEY):

    client = OpenAI(api_key=api_key)

    response = ask_scaling_question(
        client=client,
        model="gpt-5-nano-2025-08-07",
        system_prompt=GENERAL_SYSTEM_PROMPT,
        user_message="Saving is important for me. ",
    )
    print("Response given by LLM:", response)

if __name__ == "__main__":
    main()