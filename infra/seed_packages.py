"""Seed sample adventure packages into DynamoDB."""

from __future__ import annotations

import os
import sys

import boto3
from botocore.exceptions import ClientError


PACKAGES = [
    {
        "package_id": "TREK-001",
        "name": "Himalayan Ridge Trek",
        "description": "Multi-day guided trek along snow-capped ridges with alpine camps.",
        "base_price_per_person": 11000,
        "min_nights": 3,
        "max_nights": 7,
        "max_guests": 12,
        "category": "TREKKING",
        "image_url": "https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "package_id": "HILL-001",
        "name": "Tea Estate Hill Stay",
        "description": "Boutique chalet overlooking misty tea estates with curated meals.",
        "base_price_per_night": 1800,
        "min_nights": 2,
        "max_nights": 6,
        "max_guests": 4,
        "category": "HILLS_STAYCATION",
        "image_url": "https://example.com/images/tea-estate.jpg",
    },
    {
        "package_id": "JUNG-001",
        "name": "Kanha Jungle Safari",
        "description": "Certified naturalist-led jeep safaris with lakeside eco-lodging.",
        "base_price_per_person": 1400,
        "min_nights": 2,
        "max_nights": 5,
        "max_guests": 8,
        "category": "JUNGLE_SAFARI",
        "image_url": "https://example.com/images/kanha-safari.jpg",
    },
    {
        "package_id": "LODGE-001",
        "name": "Spiti Mudhouse Retreat",
        "description": "Rustic mudhouse lodging with star-studded night skies and local cuisine.",
        "base_price_per_night": 1500,
        "min_nights": 2,
        "max_nights": 5,
        "max_guests": 3,
        "category": "LODGING",
        "image_url": "https://example.com/images/spiti-mudhouse.jpg",
    },
]


def aws_enabled() -> bool:
    return os.getenv("USE_AWS", "0") == "1"


def main() -> None:
    table_name = os.getenv("DDB_PACKAGES_TABLE_NAME", "adventurestay_packages")
    region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

    if not aws_enabled():
        print("USE_AWS is not enabled. Dry-run mode; no items written.", file=sys.stderr)
        return

    dynamodb = boto3.resource("dynamodb", region_name=region)
    table = dynamodb.Table(table_name)

    try:
        table.load()
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "ResourceNotFoundException":
            raise SystemExit(f"Table {table_name} does not exist. Run bootstrap_aws.py first.")
        raise

    with table.batch_writer() as batch:
        for pkg in PACKAGES:
            batch.put_item(Item=pkg)

    print(f"Seeded {len(PACKAGES)} packages into {table_name}.")


if __name__ == "__main__":
    main()
