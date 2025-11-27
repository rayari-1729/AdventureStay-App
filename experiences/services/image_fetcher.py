"""Simple image fetcher that returns bytes for given package categories."""

from __future__ import annotations

import random
from typing import Dict, List

import requests


CATEGORY_IMAGES = {
    # ---------------------------------------------------------
    # HILLS STAYCATION — hill cabins, resorts, misty green views
    # ---------------------------------------------------------
    "HILLS_STAYCATION": [
        "https://images.unsplash.com/photo-1521119989659-a83eee488004",
        "https://images.unsplash.com/photo-1505691938895-1758d7feb511",
        "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267",
        "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee",
        "https://images.unsplash.com/photo-1482192596544-9eb780fc7f66",   # hills & cabin balcony
        "https://images.unsplash.com/photo-1501785888041-af3ef285b470",   # hill cottage
    ],

    # ---------------------------------------------------------
    # TREKKING — mountain trails, hikers, backpacks
    # ---------------------------------------------------------
    "TREKKING": [
        "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800",   # your image
        "https://images.unsplash.com/photo-1470246973918-29a93221c455",
        "https://images.unsplash.com/photo-1501785888041-af3ef285b470",
        "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429",
        "https://images.unsplash.com/photo-1500048993953-d23a436266cf",   # hikers on ridge
    ],

    # ---------------------------------------------------------
    # JUNGLE SAFARI — forest, wildlife, safari jeeps
    # ---------------------------------------------------------
    "JUNGLE_SAFARI": [
        "https://images.unsplash.com/photo-1484406566174-9da000fda645",   # your image
        "https://images.unsplash.com/photo-1470770841072-f978cf4d019e",   # tiger/jungle
        "https://images.unsplash.com/photo-1456926631375-92c8ce872def",   # elephant safari
        "https://images.unsplash.com/photo-1430026996702-608b84ce9281",   # deep forest
        "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee",   # safari jeep
    ],

    # ---------------------------------------------------------
    # LODGING — hotels, rooms, interiors, cozy stays
    # ---------------------------------------------------------
    "LODGING": [
        "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688",   # clean hotel room
        "https://images.unsplash.com/photo-1465101162946-4377e57745c3",   # cozy lodge
        "https://images.unsplash.com/photo-1554995207-c18c203602cb",      # modern bedroom
        "https://images.unsplash.com/photo-1598928506311-c55ded91a20c",   # resort exterior
        "https://images.unsplash.com/photo-1496417263034-38ec4f0b665a",   # cozy cabin interior
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


##====== from chatgpt rayari =============
# """Simple image fetcher that returns bytes for given package categories."""

# from __future__ import annotations

# import random
# from typing import Dict, List
# import requests

# # Clean, valid, category-accurate Unsplash images
# CATEGORY_IMAGES: Dict[str, List[str]] = {
#     "TREKKING": [
#         "https://images.unsplash.com/photo-1470246973918-29a93221c455",
#         "https://images.unsplash.com/photo-1500534314213-953f6b26f1fb",
#         "https://images.unsplash.com/photo-1501785888041-af3ef285b470",
#         "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429",
#         "https://images.unsplash.com/photo-1500048993953-d23a436266cf",
#     ],

#     "HILLS_STAYCATION": [
#         "https://images.unsplash.com/photo-1521119989659-a83eee488004",
#         "https://images.unsplash.com/photo-1505691938895-1758d7feb511",
#         "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267",
#         "https://images.unsplash.com/photo-1505691723518-36a1a2ef3608",
#         "https://images.unsplash.com/photo-1482192596544-5c007a81e8b1",
#     ],

#     "JUNGLE_SAFARI": [
#         "https://images.unsplash.com/photo-1470770841072-f978cf4d019e",
#         "https://images.unsplash.com/photo-1456926631375-92c8ce872def",
#         "https://images.unsplash.com/photo-1430026996702-608b84ce9281",
#         "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee",
#         "https://images.unsplash.com/photo-1441974231531-c6227db76b6e",
#     ],

#     "LODGING": [
#         "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688",
#         "https://images.unsplash.com/photo-1465101162946-4377e57745c3",
#         "https://images.unsplash.com/photo-1554995207-c18c203602cb",
#         "https://images.unsplash.com/photo-1598928506311-c55ded91a20c",
#         "https://images.unsplash.com/photo-1496417263034-38ec4f0b665a",
#     ],
# }


# def fetch_image_for_category(category: str) -> bytes:
#     """Return raw image bytes for the given category using curated Unsplash URLs."""
#     urls = CATEGORY_IMAGES.get(category.upper(), CATEGORY_IMAGES["LODGING"])
#     url = random.choice(urls) + "?auto=format&fit=crop&w=1600&q=80"
#     response = requests.get(url, timeout=15)
#     response.raise_for_status()
#     return response.content
