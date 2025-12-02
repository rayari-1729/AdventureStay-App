"""Seed sample adventure packages into DynamoDB."""

from __future__ import annotations

import os
import sys

import boto3
from botocore.exceptions import ClientError


PACKAGES = [
    # Trekking
    {
        "package_id": "TREK-001",
        "name": "Himalayan Ridge Trek",
        "description": "Multi-day guided trek along snow-capped ridges with alpine camps.",
        "base_price_per_person": 11000,
        "min_nights": 3,
        "max_nights": 7,
        "max_guests": 12,
        "category": "TREKKING",
        "location": "Manali",
        "image_url": "",
    },
    {
        "package_id": "TREK-002",
        "name": "Nilgiri Sunset Trail",
        "description": "Evening trek through Nilgiri slopes with cliff-side camping.",
        "base_price_per_person": 7500,
        "min_nights": 2,
        "max_nights": 4,
        "max_guests": 15,
        "category": "TREKKING",
        "location": "Ooty",
        "image_url": "",
    },
    {
        "package_id": "TREK-003",
        "name": "Sikkim Summit Quest",
        "description": "High-altitude route covering rhododendron forests and icy ridges.",
        "base_price_per_person": 14500,
        "min_nights": 4,
        "max_nights": 8,
        "max_guests": 8,
        "category": "TREKKING",
        "location": "Sikkim",
        "image_url": "",
    },
    {
        "package_id": "TREK-004",
        "name": "Western Ghats Monsoon Trek",
        "description": "Waterfall chasing and ridge walks with lush valley views.",
        "base_price_per_person": 6200,
        "min_nights": 2,
        "max_nights": 5,
        "max_guests": 20,
        "category": "TREKKING",
        "location": "Maharashtra",
        "image_url": "",
    },
    {
        "package_id": "TREK-005",
        "name": "Valley of Flowers Expedition",
        "description": "UNESCO trail exploring alpine meadows and glacier-fed rivers.",
        "base_price_per_person": 9900,
        "min_nights": 3,
        "max_nights": 6,
        "max_guests": 12,
        "category": "TREKKING",
        "location": "Uttarakhand",
        "image_url": "",
    },
    # Hills staycations
    {
        "package_id": "HILL-001",
        "name": "Tea Estate Hill Stay",
        "description": "Boutique chalet overlooking misty tea estates with curated meals.",
        "base_price_per_night": 1800,
        "min_nights": 2,
        "max_nights": 6,
        "max_guests": 4,
        "category": "HILLS_STAYCATION",
        "location": "Munnar",
        "image_url": "",
    },
    {
        "package_id": "HILL-002",
        "name": "Himalayan Cedar Chalet",
        "description": "Designer loft with bonfire deck and valley-facing windows.",
        "base_price_per_night": 2500,
        "min_nights": 2,
        "max_nights": 7,
        "max_guests": 5,
        "category": "HILLS_STAYCATION",
        "location": "Shimla",
        "image_url": "",
    },
    {
        "package_id": "HILL-003",
        "name": "Binsar Forest Cottage",
        "description": "Glasshouse-style stay inside an oak forest reserve.",
        "base_price_per_night": 2100,
        "min_nights": 2,
        "max_nights": 5,
        "max_guests": 4,
        "category": "HILLS_STAYCATION",
        "location": "Binsar",
        "image_url": "",
    },
    {
        "package_id": "HILL-004",
        "name": "Darjeeling Heritage Villa",
        "description": "Colonial-era villa with private butler and tea tasting.",
        "base_price_per_night": 3200,
        "min_nights": 3,
        "max_nights": 6,
        "max_guests": 6,
        "category": "HILLS_STAYCATION",
        "location": "Darjeeling",
        "image_url": "",
    },
    {
        "package_id": "HILL-005",
        "name": "Kodaikanal Artist Loft",
        "description": "Loft space with rooftop greenhouse and studio corner.",
        "base_price_per_night": 1900,
        "min_nights": 1,
        "max_nights": 4,
        "max_guests": 3,
        "category": "HILLS_STAYCATION",
        "location": "Kodaikanal",
        "image_url": "",
    },
    # Jungle safari
    {
        "package_id": "JUNG-001",
        "name": "Kanha Jungle Safari",
        "description": "Certified naturalist-led jeep safaris with lakeside eco-lodging.",
        "base_price_per_person": 1400,
        "min_nights": 2,
        "max_nights": 5,
        "max_guests": 8,
        "category": "JUNGLE_SAFARI",
        "location": "Kanha",
        "image_url": "",
    },
    {
        "package_id": "JUNG-002",
        "name": "Kaziranga Rhino Watch",
        "description": "Boat and jeep combo safaris to catch sight of grazing rhinos.",
        "base_price_per_person": 1750,
        "min_nights": 3,
        "max_nights": 6,
        "max_guests": 6,
        "category": "JUNGLE_SAFARI",
        "location": "Kaziranga",
        "image_url": "",
    },
    {
        "package_id": "JUNG-003",
        "name": "Bandipur Night Drive",
        "description": "Exclusive night drives plus day treks with birding focus.",
        "base_price_per_person": 1300,
        "min_nights": 2,
        "max_nights": 4,
        "max_guests": 10,
        "category": "JUNGLE_SAFARI",
        "location": "Bandipur",
        "image_url": "",
    },
    {
        "package_id": "JUNG-004",
        "name": "Gir Lion Expedition",
        "description": "Open jeep drives through Gir with lion tracking guides.",
        "base_price_per_person": 1600,
        "min_nights": 2,
        "max_nights": 5,
        "max_guests": 6,
        "category": "JUNGLE_SAFARI",
        "location": "Gir",
        "image_url": "",
    },
    {
        "package_id": "JUNG-005",
        "name": "Periyar Lake Safari",
        "description": "Houseboat stay and kayak safari through Periyar backwaters.",
        "base_price_per_person": 1550,
        "min_nights": 2,
        "max_nights": 4,
        "max_guests": 9,
        "category": "JUNGLE_SAFARI",
        "location": "Periyar",
        "image_url": "",
    },
    # Lodging / rustic stays
    {
        "package_id": "LODGE-001",
        "name": "Spiti Mudhouse Retreat",
        "description": "Rustic mudhouse lodging with star-studded night skies and local cuisine.",
        "base_price_per_night": 1500,
        "min_nights": 2,
        "max_nights": 5,
        "max_guests": 3,
        "category": "LODGING",
        "location": "Spiti",
        "image_url": "",
    },
    {
        "package_id": "LODGE-002",
        "name": "Coorg Forest Homestead",
        "description": "Coffee-estate homestay with DIY plantation trails.",
        "base_price_per_night": 2200,
        "min_nights": 2,
        "max_nights": 6,
        "max_guests": 5,
        "category": "LODGING",
        "location": "Coorg",
        "image_url": "",
    },
    {
        "package_id": "LODGE-003",
        "name": "Desert Camp Haven",
        "description": "Luxury tents with camel safaris and rooftop dining.",
        "base_price_per_night": 2400,
        "min_nights": 1,
        "max_nights": 4,
        "max_guests": 4,
        "category": "LODGING",
        "location": "Jaisalmer",
        "image_url": "",
    },
    {
        "package_id": "LODGE-004",
        "name": "Backwater Clay Homestay",
        "description": "Traditional clay cottages with paddle canoe and Ayurvedic meals.",
        "base_price_per_night": 2000,
        "min_nights": 1,
        "max_nights": 5,
        "max_guests": 5,
        "category": "LODGING",
        "location": "Alleppey",
        "image_url": "",
    },
    {
        "package_id": "LODGE-005",
        "name": "Kumaon Stone Lodge",
        "description": "Stone-crafted lodge with private chef and orchard walks.",
        "base_price_per_night": 2600,
        "min_nights": 2,
        "max_nights": 6,
        "max_guests": 4,
        "category": "LODGING",
        "location": "Kumaon",
        "image_url": "",
    },
]


def aws_enabled() -> bool:
    return os.getenv("USE_AWS", "0") == "1"


def main() -> None:
    table_name = os.getenv("DDB_PACKAGES_TABLE_NAME", "adventurestay_bookings")
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
