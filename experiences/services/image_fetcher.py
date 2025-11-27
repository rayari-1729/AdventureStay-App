"""Simple image fetcher that returns bytes for given package categories."""

from __future__ import annotations

import random
from typing import Dict, List

import requests


CATEGORY_IMAGES: Dict[str, List[str]] = {
    "TREKKING": [
        "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee",
        "https://images.unsplash.com/photo-1470246973918-29a93221c455",
        "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429",
        "https://images.unsplash.com/photo-1500534314213-953f6b26f1fb",
        "https://images.unsplash.com/photo-1500534314212-42a733f6f311",
        "https://images.unsplash.com/photo-1469474968028-56623f02e42e",
    ],
    "HILLS_STAYCATION": [
        "https://images.unsplash.com/photo-1505691938895-1758d7feb511",
        "https://images.unsplash.com/photo-1496417263034-38ec4f0b665a",
        "https://images.unsplash.com/photo-1505691938895-a617b73a8dbd",
        "https://images.unsplash.com/photo-1505691723518-36a1a2ef3608",
        "https://images.unsplash.com/photo-1469474968028-56623f02e42e",
    ],
    "JUNGLE_SAFARI": [
        "https://images.unsplash.com/photo-1469474968028-56623f02e42e",
        "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee",
        "https://images.unsplash.com/photo-1456926631375-92c8ce872def",
        "https://images.unsplash.com/photo-1430026996702-608b84ce9281",
        "https://images.unsplash.com/photo-1470770841072-f978cf4d019e",
    ],
    "LODGING": [
        "https://images.unsplash.com/photo-1505691938895-1758d7feb511",
        "https://images.unsplash.com/photo-1465101162946-4377e57745c3",
        "https://images.unsplash.com/photo-1469474968028-56623f02e42e",
        "https://images.unsplash.com/photo-1470246973918-29a93221c455",
        "https://images.unsplash.com/photo-1505691938895-1758d7feb511",
    ],
}


def fetch_image_for_category(category: str) -> bytes:
    """Return raw image bytes for the given category using curated Unsplash URLs."""

    urls = CATEGORY_IMAGES.get(category.upper())
    if not urls:
        urls = CATEGORY_IMAGES["LODGING"]
    url = random.choice(urls) + "?auto=format&fit=crop&w=1600&q=80"
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return response.content
