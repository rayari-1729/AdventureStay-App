"""Expose infra.bootstrap_aws as a Django management command."""

from __future__ import annotations

import os

from django.core.management.base import BaseCommand

from infra import bootstrap_aws


class Command(BaseCommand):
    help = "Create DynamoDB tables, S3 bucket, SQS queue, and SNS topic for AdventureStay."

    def handle(self, *args, **options):
        if os.getenv("USE_AWS", "0") != "1":
            self.stdout.write(self.style.WARNING("USE_AWS disabled; skipping AWS bootstrap."))
            return

        bootstrap_aws.main()
