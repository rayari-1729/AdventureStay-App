"""Management command to fetch missing package images and upload to S3."""

from __future__ import annotations

import os
import uuid

from django.core.management.base import BaseCommand

from experiences.services import dynamodb_repository, packages_repository
from experiences.services import image_fetcher
from experiences.services.aws_s3 import upload_package_image, resolve_image_url
from experiences.services import aws_enabled


class Command(BaseCommand):
    help = "Fetch missing package images and upload them to S3."

    def handle(self, *args, **options):
        if not aws_enabled():
            self.stdout.write(self.style.WARNING("USE_AWS disabled; skipping image refresh."))
            return

        packages = dynamodb_repository.list_packages_from_dynamodb()
        total = len(packages)
        updated = 0
        self.stdout.write(f"Found {total} packages")

        for package in packages:
            code = package.get("package_code")
            image_url = package.get("image_url", "")
            if image_url and image_url.startswith("http"):
                self.stdout.write(f"{code} -> already has image, skipped")
                continue

            category = package.get("category", "LODGING")
            image_bytes = image_fetcher.fetch_image_for_category(category)
            filename = f"{code.lower()}-{uuid.uuid4().hex}.jpg"
            s3_url = upload_package_image(image_bytes, filename)
            packages_repository.update_package_image_url(code, s3_url)
            self.stdout.write(f"{code} -> updated image {s3_url}")
            updated += 1

        self.stdout.write(self.style.SUCCESS(f"Updated {updated} packages."))
