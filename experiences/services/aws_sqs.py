"""SQS helpers for booking notifications."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from django.conf import settings

from . import aws_enabled, log_local_fallback

logger = logging.getLogger(__name__)


def send_booking_created_message(booking_data: Dict[str, Any]) -> None:
    queue_url = getattr(settings, "SQS_BOOKING_QUEUE_URL", "")
    if not aws_enabled() or not queue_url:
        log_local_fallback("sqs", {"queue_url": queue_url})
        return

    client = boto3.client("sqs", region_name=getattr(settings, "AWS_REGION", None))
    try:
        client.send_message(QueueUrl=queue_url, MessageBody=json.dumps(booking_data))
    except (BotoCoreError, ClientError) as exc:
        logger.exception("Failed to send booking message to SQS: %s", exc)
