"""DynamoDB repository helpers."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from django.conf import settings

from . import aws_enabled, log_local_fallback

logger = logging.getLogger(__name__)


def _get_table(table_name: str):
    if not aws_enabled():
        log_local_fallback("dynamodb")
        return None

    if not table_name:
        logger.warning("DynamoDB table name missing; skipping call.")
        return None

    region = getattr(settings, "AWS_REGION", None)
    resource = boto3.resource("dynamodb", region_name=region)
    return resource.Table(table_name)


def save_booking_to_dynamodb(booking_data: Dict[str, Any]) -> None:
    table_name = getattr(settings, "DDB_BOOKINGS_TABLE_NAME", "")
    table = _get_table(table_name)
    if not table:
        return

    try:
        table.put_item(Item=booking_data)
    except (BotoCoreError, ClientError) as exc:
        logger.exception("Failed to save booking to DynamoDB: %s", exc)


def list_bookings_for_package(package_code: str) -> List[Dict[str, Any]]:
    table_name = getattr(settings, "DDB_BOOKINGS_TABLE_NAME", "")
    table = _get_table(table_name)
    if not table:
        return []

    try:
        response = table.query(
            IndexName="package_code-index",
            KeyConditionExpression="package_code = :pkg",
            ExpressionAttributeValues={":pkg": package_code},
        )
        return response.get("Items", [])
    except (BotoCoreError, ClientError) as exc:
        logger.exception("Failed to fetch bookings from DynamoDB: %s", exc)
        return []
