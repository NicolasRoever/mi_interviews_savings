from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Iterable
from openai import AsyncOpenAI
import asyncio
import time
import logging
from core.auxiliary import fill_prompt_with_interview_v002, get_step_by_question_name
from core.error_handling import check_data_is_not_empty


@dataclass(frozen=True)
class CallPlan:
    delay_s: float
    model: str
    max_output_tokens: int
    reasoning_effort: str
    per_request_timeout_s: float


async def openai_call(
    client: AsyncOpenAI, prompt: str, plan: CallPlan
) -> Tuple[str, Any, CallPlan, float]:
    """
    Perform one OpenAI call with optional start delay and a per-request timeout.
    Returns (text, raw_response, plan, elapsed_seconds).
    """
    if plan.delay_s > 0:
        await asyncio.sleep(plan.delay_s)

    start = time.perf_counter()
    logging.info("Starting call model=%s (delay=%.2fs)", plan.model, plan.delay_s)

    resp = await asyncio.wait_for(
        client.responses.create(
            model=plan.model,
            input=prompt,
            reasoning={"effort": plan.reasoning_effort},
            max_output_tokens=plan.max_output_tokens,
        ),
        timeout=plan.per_request_timeout_s,
    )

    text = (getattr(resp, "output_text", None) or "").strip()
    elapsed = time.perf_counter() - start
    logging.info("Completed model=%s in %.3fs", plan.model, elapsed)
    return text, resp, plan, elapsed


async def race_first(tasks: List["asyncio.Task"]) -> Tuple[str, Any, CallPlan, float]:
    """
    Wait for the first task that completes successfully.
    Immediately cancel all remaining tasks when a success occurs.
    If a finished task raised, keep waiting for another to succeed.
    If all tasks fail, re-raise the first error.
    """
    pending = set(tasks)
    first_error: BaseException | None = None

    while pending:
        done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)

        for finished in done:
            try:
                result = await finished  # (text, resp, plan, elapsed)

                # On success: cancel remaining tasks ASAP
                for t in pending:
                    t.cancel()
                await asyncio.gather(*pending, return_exceptions=True)

                return result

            except asyncio.CancelledError:
                # Ignore; continue to look for a successful finisher
                continue
            except BaseException as e:
                # Record the first error, keep waiting for others
                if first_error is None:
                    first_error = e
                logging.warning("A hedged call failed: %r", e)

    # If we’re here, every task failed or was cancelled
    if first_error is not None:
        raise first_error
    raise RuntimeError("Hedge race ended with no tasks (unexpected).")


async def call_openai_responses_hedged(
    client: AsyncOpenAI,
    *,
    prompt: str,
    primary_model: str = "gpt-5-nano-2025-08-07",
    fallback_model: str = "gpt-5-nano-2025-08-07",
    hedge_delay_s: float = 2.0,
    max_output_tokens: int = 200,
    reasoning_effort: str = "minimal",
    per_request_timeout_s: float = 12.0,
) -> Tuple[str, Any, CallPlan]:
    """
    Run primary immediately and fallback after hedge_delay_s.
    Return the first result. (race_first handles cancellations.)
    """
    plans = [
        CallPlan(
            0.0,
            primary_model,
            max_output_tokens,
            reasoning_effort,
            per_request_timeout_s,
        ),
        CallPlan(
            hedge_delay_s,
            fallback_model,
            max_output_tokens,
            reasoning_effort,
            per_request_timeout_s,
        ),
    ]

    tasks = [asyncio.create_task(openai_call(client, prompt, plan)) for plan in plans]
    text, resp, plan, elapsed = await race_first(tasks)

    logging.info(
        "Winner model=%s (delay=%.2fs, elapsed=%.3fs)",
        plan.model,
        plan.delay_s,
        elapsed,
    )
    return text, resp, plan
