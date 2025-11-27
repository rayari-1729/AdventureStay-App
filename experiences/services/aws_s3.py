"""AWS S3 helpers used for optional media hosting."""

from __future__ import annotations

import boto3
from django.conf import settings

from . import aws_enabled, log_local_fallback


def get_s3_client():
    if not aws_enabled():
        log_local_fallback("s3")
        return None

    region = getattr(settings, "AWS_REGION", None)
    return boto3.client("s3", region_name=region)


def build_package_image_url(package_code: str) -> str:
    bucket = getattr(settings, "S3_BUCKET_NAME", "")
    region = getattr(settings, "AWS_REGION", "ap-south-1")
    if not bucket:
        return ""
    return f"https://{bucket}.s3.{region}.amazonaws.com/packages/{package_code}.jpg"


# def resolve_image_url(image_url_or_key: str | None) -> str:
#     """Return a usable image URL based on a stored URL or S3 object key."""

#     if not image_url_or_key:
#         return ""

#     normalized = image_url_or_key.strip()
#     if normalized.startswith("http://") or normalized.startswith("https://"):
#         return normalized

#     bucket = getattr(settings, "S3_BUCKET_NAME", "")
#     region = getattr(settings, "AWS_REGION", "ap-south-1")
#     if not bucket:
#         log_local_fallback("s3", {"image_key": normalized})
#         return normalized

#     return f"https://{bucket}.s3.{region}.amazonaws.com/{normalized.lstrip('/')}"

def resolve_image_url(image_key: str | None) -> str:
    """Generate a presigned URL for private S3 objects."""
    if not image_key:
        return ""

    # If it's already a full URL (e.g., Unsplash), return as-is
    if image_key.startswith("http://") or image_key.startswith("https://"):
        return image_key

    bucket = getattr(settings, "S3_BUCKET_NAME", "")
    if not bucket:
        return image_key

    s3 = boto3.client("s3")

    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": image_key},
        ExpiresIn=3600 * 12,   # 12 hours
    )

    return url


# def upload_package_image(image_bytes: bytes, filename: str) -> str:
#     """Upload image bytes to S3 under packages/ and return the public URL."""

#     client = get_s3_client()
#     bucket = getattr(settings, "S3_BUCKET_NAME", "")
#     if not client or not bucket:
#         log_local_fallback("s3-upload", {"filename": filename})
#         raise RuntimeError("S3 upload unavailable.")

#     key = f"packages/{filename}"
#     client.put_object(Bucket=bucket, Key=key, Body=image_bytes, ContentType="image/jpeg",) #ACL="public-read",)
#     region = getattr(settings, "AWS_REGION", "ap-south-1")
#     return f"https://{bucket}.s3.{region}.amazonaws.com/{key}"

def upload_package_image(image_bytes: bytes, filename: str) -> str:
    client = boto3.client("s3")
    bucket = settings.S3_BUCKET_NAME
    key = f"packages/{filename}"

    client.put_object(
        Bucket=bucket,
        Key=key,
        Body=image_bytes,
        ContentType="image/jpeg",
    )

    # return ONLY key, not URL
    return key



def get_package_image_url(package_code: str) -> str | None:
    """Return an S3 image URL if AWS is enabled and configured."""

    if not aws_enabled():
        log_local_fallback("s3", {"package_code": package_code})
        return None

    url = build_package_image_url(package_code)
    if not url:
        log_local_fallback("s3", {"package_code": package_code})
        return None
    return url
