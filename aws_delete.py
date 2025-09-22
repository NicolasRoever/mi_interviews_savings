from boto3 import resource
from argparse import ArgumentParser
from csv import DictWriter
from pydantic import validate_call
import logging
from typing import Optional


@validate_call
def delete_all_sessions(table_name: str, limit: Optional[int] = None) -> None:
    """
    Delete all entries in a DynamoDB table.

    Args:
        table_name (str): Name of the DynamoDB table.
        limit (Optional[int]): Maximum number of items to delete (for testing).
    """
    table = resource("dynamodb").Table(table_name)
    last_eval = None
    deleted_count = 0

    while True:
        scan_kwargs = {"ExclusiveStartKey": last_eval} if last_eval else {}
        response = table.scan(**scan_kwargs)

        items = response.get("Items", [])
        for item in items:
            key = {"session_id": item["session_id"]}
            table.delete_item(Key=key)
            deleted_count += 1
            logging.info(f"Deleted session {item['session_id']}")

            if limit and deleted_count >= limit:
                logging.info(
                    f"Stopped after deleting {deleted_count} items (limit reached)."
                )
                return

        if not response.get("LastEvaluatedKey"):
            break
        last_eval = response["LastEvaluatedKey"]

    logging.info(f"Deleted {deleted_count} items from table '{table_name}'.")
