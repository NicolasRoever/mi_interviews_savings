import logging
from typing import Any, Dict, List


def check_data_is_not_empty(data: Any, name: str = "data") -> None:
    if not data:
        logging.error(f"Data check failed: {name} is empty.")
        raise ValueError(f"{name} must not be empty.")
