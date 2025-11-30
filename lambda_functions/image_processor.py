import json
import io
import logging
import os
from typing import Any, Dict

import boto3
from PIL import Image

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

DDB_TABLE = os.getenv("DDB_PACKAGES_TABLE_NAME", "adventurestay_packages")
THUMB_PREFIX = os.getenv("THUMBNAIL_PREFIX", "thumbnails/")
THUMB_WIDTH = int(os.getenv("THUMBNAIL_WIDTH", "300"))


def handler(event: Dict[str, Any], _context) -> None:
    logger.info("Received event: %s", event)

    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]

        if not key.startswith("packages/"):
            logger.info("Skipping non-package key: %s", key)
            continue

        try:
            _process_image(bucket, key)
        except Exception:
            logger.exception("Failed to process %s/%s", bucket, key)


def _process_image(bucket: str, key: str) -> None:
    logger.info("Processing s3://%s/%s", bucket, key)

    # download
    original = s3.get_object(Bucket=bucket, Key=key)
    image_bytes = original["Body"].read()

    # create thumb
    thumb_bytes = _create_thumbnail(image_bytes)
    thumb_key = f"{THUMB_PREFIX}{os.path.basename(key)}"

    # upload (NO ACL!)
    s3.put_object(
        Bucket=bucket,
        Key=thumb_key,
        Body=thumb_bytes,
        ContentType="image/jpeg",
    )
    logger.info("Uploaded thumbnail to s3://%s/%s", bucket, thumb_key)

    # extract package_code TREK-001 from trek-001-abc123.jpg
    base = os.path.basename(key).split("-")[0:2]
    package_code = "-".join(base).upper()

    # update DynamoDB
    if package_code and DDB_TABLE:
        table = dynamodb.Table(DDB_TABLE)
        table.update_item(
            Key={"package_code": package_code},
            UpdateExpression="SET thumbnail_key = :thumb",
            ExpressionAttributeValues={":thumb": thumb_key},
        )
        logger.info("Updated DynamoDB %s thumbnail %s", package_code, thumb_key)


def _create_thumbnail(image_bytes: bytes) -> bytes:
    with Image.open(io.BytesIO(image_bytes)) as img:
        img = img.convert("RGB")
        img.thumbnail((THUMB_WIDTH, THUMB_WIDTH * 10000), Image.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)
        return buffer.read()
