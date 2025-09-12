import logging
from typing import Any, Dict, List
from openai import APIStatusError, AuthenticationError, APIConnectionError


def check_data_is_not_empty(data: Any, name: str = "data") -> None:
    if not data:
        logging.error(f"Data check failed: {name} is empty.")
        raise ValueError(f"{name} must not be empty.")


def handle_openai_error(e: Exception) -> None:
    """
    Unified error handler for OpenAI exceptions.
    Logs details using the standard logging module, then re-raises.
    """
    if isinstance(e, APIStatusError):
        try:
            details = e.response.json()
        except Exception:
            details = getattr(e, "response", None)
        logging.error(
            "OpenAI APIStatusError %s: %s", getattr(e, "status_code", "?"), details
        )
    elif isinstance(e, AuthenticationError):
        logging.error("OpenAI AuthenticationError: %s", e)
    elif isinstance(e, APIConnectionError):
        logging.error("OpenAI APIConnectionError: %s", e)
    else:
        logging.error("OpenAI unexpected error: %s", e)

    raise e
