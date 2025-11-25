"""DynamoDB repository helpers."""

from __future__ import annotations

import logging
from typing import Any, Dict, List
from decimal import Decimal 

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from django.conf import settings

from ..models import AdventureBookingModel
from . import aws_enabled, log_local_fallback

logger = logging.getLogger(__name__)


def get_dynamodb_client():
    """Return a DynamoDB resource when AWS integration is active."""

    if not aws_enabled():
        log_local_fallback("dynamodb")
        return None

    region = getattr(settings, "AWS_REGION", None)
    return boto3.resource("dynamodb", region_name=region)


def _serialize_booking(booking: AdventureBookingModel) -> Dict[str, Any]:
    from decimal import Decimal  # or use the top-level import

    total_price = booking.total_price

    # Ensure total_price is Decimal for DynamoDB
    if total_price is None:
        price_decimal = Decimal("0")
    elif isinstance(total_price, Decimal):
        price_decimal = total_price
    else:
        # Covers float, str, etc.
        price_decimal = Decimal(str(total_price))

    return {
        "booking_id": str(booking.id),
        "package_code": booking.package.package_code,
        "package_name": booking.package.name,
        "category": booking.package.category,
        "start_date": booking.start_date.isoformat(),
        "end_date": booking.end_date.isoformat(),
        "num_guests": booking.num_guests,  # int is fine
        "total_price": price_decimal,
        "created_at": booking.created_at.isoformat(),
    }


def save_booking_to_dynamodb(booking: AdventureBookingModel) -> None:
    """Persist the booking to the configured DynamoDB table."""

    table_name = getattr(settings, "DDB_BOOKINGS_TABLE_NAME", "")
    if not table_name:
        logger.warning("DDB_BOOKINGS_TABLE_NAME not set; skipping DynamoDB write.")
        return

    client = get_dynamodb_client()
    if not client:
        return

    table = client.Table(table_name)
    item = _serialize_booking(booking)
    try:
        table.put_item(Item=item)
        logger.info("Stored booking %s in DynamoDB table %s", item["booking_id"], table_name)
    except (BotoCoreError, ClientError) as exc:
        logger.exception("Failed to save booking to DynamoDB: %s", exc)


def list_bookings_for_package(package_code: str) -> List[Dict[str, Any]]:
    """Fetch bookings for a given package from DynamoDB (best-effort)."""

    table_name = getattr(settings, "DDB_BOOKINGS_TABLE_NAME", "")
    if not table_name:
        logger.warning("DDB_BOOKINGS_TABLE_NAME not set; cannot query DynamoDB.")
        return []

    client = get_dynamodb_client()
    if not client:
        return []

    table = client.Table(table_name)
    try:
        response = table.scan(
            FilterExpression="package_code = :pkg",
            ExpressionAttributeValues={":pkg": package_code},
        )
        return response.get("Items", [])
    except (BotoCoreError, ClientError) as exc:
        logger.exception("Failed to fetch bookings from DynamoDB: %s", exc)
        return []
