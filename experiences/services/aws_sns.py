"""SNS helpers for booking confirmations."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from django.conf import settings

from . import aws_enabled, log_local_fallback

logger = logging.getLogger(__name__)


def publish_booking_confirmation(booking_data: Dict[str, Any]) -> None:
    topic_arn = getattr(settings, "SNS_BOOKING_TOPIC_ARN", "")
    if not aws_enabled() or not topic_arn:
        log_local_fallback("sns", {"topic_arn": topic_arn})
        return

    client = boto3.client("sns", region_name=getattr(settings, "AWS_REGION", None))
    try:
        client.publish(
            TopicArn=topic_arn,
            Message=json.dumps(booking_data),
            Subject="AdventureStay Booking Confirmation",
        )
    except (BotoCoreError, ClientError) as exc:
        logger.exception("Failed to publish booking to SNS: %s", exc)
