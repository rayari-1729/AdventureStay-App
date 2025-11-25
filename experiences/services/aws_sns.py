"""SNS helpers for booking confirmations."""

from __future__ import annotations

import json
import logging

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from django.conf import settings

from ..models import AdventureBookingModel
from . import aws_enabled, log_local_fallback

logger = logging.getLogger(__name__)


def get_sns_client():
    if not aws_enabled():
        log_local_fallback("sns")
        return None

    region = getattr(settings, "AWS_REGION", None)
    return boto3.client("sns", region_name=region)


def publish_booking_confirmation(booking: AdventureBookingModel) -> None:
    """Publish a confirmation notification for the booking."""

    topic_arn = getattr(settings, "SNS_BOOKING_TOPIC_ARN", "")
    if not topic_arn:
        logger.warning("SNS_BOOKING_TOPIC_ARN not set; skipping SNS notification.")
        return

    client = get_sns_client()
    if not client:
        return

    message = {
        "package": booking.package.name,
        "location": booking.package.location,
        "start_date": booking.start_date.isoformat(),
        "end_date": booking.end_date.isoformat(),
        "num_guests": booking.num_guests,
        "total_price": float(booking.total_price),
        "booking_id": str(booking.id),
    }

    try:
        response = client.publish(
            TopicArn=topic_arn,
            Subject="AdventureStay Booking Confirmed",
            Message=json.dumps(message),
        )
        logger.info("Published booking confirmation to SNS. MessageId=%s", response.get("MessageId"))
    except (BotoCoreError, ClientError) as exc:
        logger.exception("Failed to publish booking to SNS: %s", exc)
