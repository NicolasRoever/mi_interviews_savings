from openai import OpenAI
from config import OPENAI_API_KEY
from llm import ask_scaling_question,openai_generate_mi_turn, run_flow, get_user_reply_cli
from interview_guide import STEPS, GLOBAL_MI_SYSTEM_PROMPT
from typing import Dict, Any, Optional, Tuple

def main(api_key=OPENAI_API_KEY):

    client = OpenAI(api_key=api_key)
    ctx = run_flow(
        client=client,
        steps=STEPS,
        get_user_reply=get_user_reply_cli,
        ctx={},
    )

    print("\n--- SESSION CONTEXT ---")
    for k, v in ctx.items():
        if k != "history":
            print(f"{k}: {v}")

    print("\n--- HISTORY ---")
    for m in ctx["history"]:
        print(m)

    
if __name__ == "__main__":
    main()
    