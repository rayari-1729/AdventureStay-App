"""Service helpers shared across the experiences app."""

from __future__ import annotations

import logging
from typing import Any, Dict

from django.conf import settings

logger = logging.getLogger(__name__)


def aws_enabled() -> bool:
    """Return True when AWS calls should be attempted."""

    return getattr(settings, "USE_AWS", False)


def log_local_fallback(service_name: str, extra: Dict[str, Any] | None = None) -> None:
    """Log a message describing why a cloud call was skipped."""

    logger.info("%s skipped (local fallback). Details: %s", service_name, extra or {})

