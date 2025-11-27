"""Unified package repository handling AWS + local fallback."""

from __future__ import annotations

from decimal import Decimal
from typing import Dict, List, Optional

from django.conf import settings

from ..models import AdventurePackageModel
from . import aws_enabled
from . import dynamodb_repository


def _should_use_dynamodb() -> bool:
    return aws_enabled() and bool(getattr(settings, "DDB_PACKAGES_TABLE_NAME", ""))


def get_all_packages() -> List[Dict[str, object]]:
    """Return package DTOs sourced from DynamoDB when enabled or Django ORM otherwise."""

    if _should_use_dynamodb():
        packages = dynamodb_repository.list_packages_from_dynamodb()
        if packages:
            return packages
    return [_model_to_dto(pkg) for pkg in AdventurePackageModel.objects.filter(is_active=True)]


def get_package_by_code(package_code: str) -> Optional[Dict[str, object]]:
    if _should_use_dynamodb():
        dto = dynamodb_repository.get_package_from_dynamodb(package_code)
        if dto:
            return dto

    try:
        package = AdventurePackageModel.objects.get(package_code=package_code, is_active=True)
    except AdventurePackageModel.DoesNotExist:
        return None
    return _model_to_dto(package)


def ensure_package_model(dto: Dict[str, object]) -> AdventurePackageModel:
    """Ensure a local AdventurePackageModel exists so bookings can FK safely."""

    base_price_per_night = dto.get("base_price_per_night")
    base_price_per_person = dto.get("base_price_per_person")

    defaults = {
        "category": dto.get("category", AdventurePackageModel.LODGING),
        "name": dto.get("name", ""),
        "location": dto.get("location", ""),
        "base_price_per_night": _to_decimal_for_model(base_price_per_night),
        "base_price_per_person": _to_decimal_for_model(base_price_per_person),
        "max_guests": dto.get("max_guests") or 1,
        "min_nights": dto.get("min_nights") or 1,
        "max_nights": dto.get("max_nights") or 7,
        "includes_meals": dto.get("includes_meals", False),
        "includes_guide": dto.get("includes_guide", False),
        "image_url": dto.get("image_url", ""),
        "is_active": True,
    }

    package, _ = AdventurePackageModel.objects.update_or_create(
        package_code=dto.get("package_code"), defaults=defaults
    )
    return package


def _model_to_dto(package: AdventurePackageModel) -> Dict[str, object]:
    return {
        "package_code": package.package_code,
        "category": package.category,
        "name": package.name,
        "description": "",
        "location": package.location,
        "base_price_per_night": _price_to_number(package.base_price_per_night),
        "base_price_per_person": _price_to_number(package.base_price_per_person),
        "min_nights": package.min_nights,
        "max_nights": package.max_nights,
        "max_guests": package.max_guests,
        "image_url": package.image_url,
        "includes_meals": package.includes_meals,
        "includes_guide": package.includes_guide,
    }


def _to_decimal_for_model(value):
    if value is None or value == "":
        return None
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _price_to_number(value):
    if value is None or value == "":
        return None
    if isinstance(value, Decimal):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def update_package_image_url(package_code: str, new_url: str) -> None:
    """Persist updated image URL to DynamoDB when AWS mode is active."""

    if not _should_use_dynamodb():
        return
    table = dynamodb_repository._package_table()  # use existing helper
    if not table:
        return
    table.update_item(
        Key={"package_id": package_code},
        UpdateExpression="SET image_url = :url",
        ExpressionAttributeValues={":url": new_url},
    )
