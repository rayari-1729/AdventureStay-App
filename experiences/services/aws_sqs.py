"""SQS helpers for booking notifications."""

from __future__ import annotations

import json
import logging

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from django.conf import settings

from ..models import AdventureBookingModel
from . import aws_enabled, log_local_fallback

logger = logging.getLogger(__name__)


def get_sqs_client():
    if not aws_enabled():
        log_local_fallback("sqs")
        return None

    region = getattr(settings, "AWS_REGION", None)
    return boto3.client("sqs", region_name=region)


def send_booking_created_message(booking: AdventureBookingModel) -> None:
    """Send a booking_created event to the configured SQS queue."""

    queue_url = getattr(settings, "SQS_BOOKING_QUEUE_URL", "")
    if not queue_url:
        logger.warning("SQS_BOOKING_QUEUE_URL not set; skipping SQS publish.")
        return

    client = get_sqs_client()
    if not client:
        return

    message = {
        "event_type": "booking_created",
        "booking_id": str(booking.id),
        "package_code": booking.package.package_code,
        "category": booking.package.category,
        "start_date": booking.start_date.isoformat(),
        "end_date": booking.end_date.isoformat(),
        "num_guests": booking.num_guests,
        "total_price": float(booking.total_price),
    }

    try:
        response = client.send_message(QueueUrl=queue_url, MessageBody=json.dumps(message))
        logger.info("Sent booking_created message to SQS. MessageId=%s", response.get("MessageId"))
    except (BotoCoreError, ClientError) as exc:
        logger.exception("Failed to send booking message to SQS: %s", exc)
