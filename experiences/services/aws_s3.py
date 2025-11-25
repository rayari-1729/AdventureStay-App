"""AWS S3 helpers used for optional media hosting."""

from __future__ import annotations

from django.conf import settings

from . import aws_enabled, log_local_fallback


def get_package_image_url(package_code: str) -> str | None:
    """Return an S3 image URL if AWS is enabled and configured."""

    bucket = getattr(settings, "S3_BUCKET_NAME", "")
    region = getattr(settings, "AWS_REGION", "ap-south-1")

    if not aws_enabled() or not bucket:
        log_local_fallback("s3", {"package_code": package_code})
        return None

    return f"https://{bucket}.s3.{region}.amazonaws.com/packages/{package_code}.jpg"
