"""Management command to seed DynamoDB packages using the infra dataset."""

from __future__ import annotations

import os

import boto3
from botocore.exceptions import ClientError
from django.core.management.base import BaseCommand

from infra.seed_packages import PACKAGES


class Command(BaseCommand):
    help = "Seed the adventurestay_packages DynamoDB table with default packages."

    def handle(self, *args, **options):
        if os.getenv("USE_AWS", "0") != "1":
            self.stdout.write(self.style.WARNING("USE_AWS disabled; skipping seed."))
            return

        table_name = os.getenv("DDB_PACKAGES_TABLE_NAME", "adventurestay_packages")
        region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        dynamodb = boto3.resource("dynamodb", region_name=region)
        table = dynamodb.Table(table_name)

        try:
            table.load()
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "ResourceNotFoundException":
                raise SystemExit(
                    f"Table {table_name} does not exist. Run infra/bootstrap_aws.py first."
                )
            raise

        with table.batch_writer() as batch:
            for pkg in PACKAGES:
                batch.put_item(Item=pkg)

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(PACKAGES)} packages into {table_name}."))
