"""DynamoDB repository helpers."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from decimal import Decimal

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from django.conf import settings

from ..models import AdventureBookingModel
from . import aws_enabled, log_local_fallback
from .aws_s3 import resolve_image_url

logger = logging.getLogger(__name__)


def get_dynamodb_client():
    """Return a DynamoDB resource when AWS integration is active."""

    if not aws_enabled():
        log_local_fallback("dynamodb")
        return None

    region = getattr(settings, "AWS_REGION", None)
    return boto3.resource("dynamodb", region_name=region)


def _serialize_booking(booking: AdventureBookingModel) -> Dict[str, Any]:
    total_price = booking.total_price
    if total_price is None:
        price_decimal = Decimal("0")
    elif isinstance(total_price, Decimal):
        price_decimal = total_price
    else:
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


def _package_table():
    table_name = getattr(settings, "DDB_PACKAGES_TABLE_NAME", "")
    if not table_name:
        logger.warning("DDB_PACKAGES_TABLE_NAME not set; skipping package lookup.")
        return None

    client = get_dynamodb_client()
    if not client:
        return None

    return client.Table(table_name)


def _coerce_decimal(value):
    if isinstance(value, Decimal):
        return float(value)
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_int(value, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    return bool(value)


def _build_package_dto(item: Dict[str, Any]) -> Dict[str, Any]:
    if not item:
        return {}

    image_url = resolve_image_url(item.get("image_url"))
    dto = {
        "package_code": item.get("package_id") or item.get("package_code"),
        "category": item.get("category", ""),
        "name": item.get("name", ""),
        "description": item.get("description", ""),
        "location": item.get("location", item.get("region", "Remote Wilderness")),
        "base_price_per_night": _coerce_decimal(item.get("base_price_per_night")),
        "base_price_per_person": _coerce_decimal(item.get("base_price_per_person")),
        "min_nights": _safe_int(item.get("min_nights"), 1),
        "max_nights": _safe_int(item.get("max_nights"), 7),
        "max_guests": _safe_int(item.get("max_guests"), 4),
        "image_url": image_url,
        "includes_meals": _safe_bool(item.get("includes_meals", False)),
        "includes_guide": _safe_bool(item.get("includes_guide", False)),
    }
    return dto


def list_packages_from_dynamodb() -> List[Dict[str, Any]]:
    table = _package_table()
    if not table:
        return []

    try:
        response = table.scan()
    except (BotoCoreError, ClientError) as exc:
        logger.exception("Failed to scan packages table: %s", exc)
        return []

    items = response.get("Items", [])
    return [_build_package_dto(item) for item in items if item]


def get_package_from_dynamodb(package_code: str) -> Optional[Dict[str, Any]]:
    table = _package_table()
    if not table:
        return None

    try:
        response = table.get_item(Key={"package_id": package_code})
    except (BotoCoreError, ClientError) as exc:
        logger.exception("Failed to load package %s from DynamoDB: %s", package_code, exc)
        return None

    item = response.get("Item")
    if not item:
        return None
    return _build_package_dto(item)

##======== from chatgpt rayari ========
# """DynamoDB repository helpers."""

# from __future__ import annotations

# import logging
# from typing import Any, Dict, List, Optional
# from decimal import Decimal

# import boto3
# from botocore.exceptions import BotoCoreError, ClientError
# from django.conf import settings

# from ..models import AdventureBookingModel
# from . import aws_enabled, log_local_fallback

# logger = logging.getLogger(__name__)


# def get_dynamodb_client():
#     """Return a DynamoDB resource when AWS integration is active."""
#     if not aws_enabled():
#         log_local_fallback("dynamodb")
#         return None

#     region = getattr(settings, "AWS_REGION", None)
#     return boto3.resource("dynamodb", region_name=region)


# # -------------------------------------------------------------
# # BOOKING SERIALIZATION & SAVING
# # -------------------------------------------------------------

# def _serialize_booking(booking: AdventureBookingModel) -> Dict[str, Any]:
#     total_price = booking.total_price
#     if total_price is None:
#         price_decimal = Decimal("0")
#     elif isinstance(total_price, Decimal):
#         price_decimal = total_price
#     else:
#         price_decimal = Decimal(str(total_price))

#     return {
#         "booking_id": str(booking.id),
#         "package_code": booking.package.package_code,
#         "package_name": booking.package.name,
#         "category": booking.package.category,
#         "start_date": booking.start_date.isoformat(),
#         "end_date": booking.end_date.isoformat(),
#         "num_guests": booking.num_guests,
#         "total_price": price_decimal,
#         "created_at": booking.created_at.isoformat(),
#     }


# def save_booking_to_dynamodb(booking: AdventureBookingModel) -> None:
#     """Persist the booking to the configured DynamoDB table."""
#     table_name = getattr(settings, "DDB_BOOKINGS_TABLE_NAME", "")
#     if not table_name:
#         logger.warning("DDB_BOOKINGS_TABLE_NAME not set; skipping DynamoDB write.")
#         return

#     client = get_dynamodb_client()
#     if not client:
#         return

#     table = client.Table(table_name)
#     item = _serialize_booking(booking)

#     try:
#         table.put_item(Item=item)
#         logger.info("Stored booking %s in DynamoDB table %s", item["booking_id"], table_name)
#     except (BotoCoreError, ClientError) as exc:
#         logger.exception("Failed to save booking to DynamoDB: %s", exc)


# # -------------------------------------------------------------
# # PACKAGE TABLE HELPERS
# # -------------------------------------------------------------

# def _package_table():
#     table_name = getattr(settings, "DDB_PACKAGES_TABLE_NAME", "")
#     if not table_name:
#         logger.warning("DDB_PACKAGES_TABLE_NAME not set; skipping package lookup.")
#         return None

#     client = get_dynamodb_client()
#     if not client:
#         return None

#     return client.Table(table_name)


# def _coerce_decimal(value):
#     if isinstance(value, Decimal):
#         return float(value)
#     if value in (None, ""):
#         return None
#     try:
#         return float(value)
#     except (TypeError, ValueError):
#         return None


# def _safe_int(value, default: int) -> int:
#     try:
#         return int(value)
#     except (TypeError, ValueError):
#         return default


# def _safe_bool(value) -> bool:
#     if isinstance(value, bool):
#         return value
#     return bool(value)


# def _build_package_dto(item: Dict[str, Any]) -> Dict[str, Any]:
#     """Convert raw DynamoDB package record into a clean DTO."""

#     if not item:
#         return {}

#     dto = {
#         # FIX: always use package_code (your DynamoDB schema)
#         "package_code": item.get("package_code"),

#         "category": item.get("category", ""),
#         "name": item.get("name", ""),
#         "description": item.get("description", ""),
#         "location": item.get("location", item.get("region", "Remote Wilderness")),
#         "base_price_per_night": _coerce_decimal(item.get("base_price_per_night")),
#         "base_price_per_person": _coerce_decimal(item.get("base_price_per_person")),
#         "min_nights": _safe_int(item.get("min_nights"), 1),
#         "max_nights": _safe_int(item.get("max_nights"), 7),
#         "max_guests": _safe_int(item.get("max_guests"), 4),

#         # FIX: do NOT force S3 resolution; use raw URLs
#         "image_url": item.get("image_url", ""),

#         "includes_meals": _safe_bool(item.get("includes_meals", False)),
#         "includes_guide": _safe_bool(item.get("includes_guide", False)),
#     }

#     return dto


# # -------------------------------------------------------------
# # PUBLIC API
# # -------------------------------------------------------------

# def list_packages_from_dynamodb() -> List[Dict[str, Any]]:
#     table = _package_table()
#     if not table:
#         return []

#     try:
#         response = table.scan()
#     except (BotoCoreError, ClientError) as exc:
#         logger.exception("Failed to scan packages table: %s", exc)
#         return []

#     items = response.get("Items", [])
#     return [_build_package_dto(item) for item in items if item]


# def get_package_from_dynamodb(package_code: str) -> Optional[Dict[str, Any]]:
#     table = _package_table()
#     if not table:
#         return None

#     try:
#         # FIX: correct the key
#         response = table.get_item(Key={"package_code": package_code})
#     except (BotoCoreError, ClientError) as exc:
#         logger.exception("Failed to load package %s from DynamoDB: %s", package_code, exc)
#         return None

#     item = response.get("Item")
#     if not item:
#         return None

#     return _build_package_dto(item)

