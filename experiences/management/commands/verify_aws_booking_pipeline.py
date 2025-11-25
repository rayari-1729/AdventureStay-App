"""Management command to manually test AWS integrations."""

from __future__ import annotations

import logging
from datetime import date, timedelta

from django.core.management.base import BaseCommand

from experiences.models import AdventureBookingModel, AdventurePackageModel
from experiences.services import aws_sns, aws_sqs, dynamodb_repository

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sends a sample booking through the AWS pipeline (DynamoDB, SQS, SNS)."

    def handle(self, *args, **options):
        package, _ = AdventurePackageModel.objects.get_or_create(
            package_code="VERIFY-PACKAGE",
            defaults={
                "category": AdventurePackageModel.LODGING,
                "name": "Verification Lodge",
                "location": "Cloud9",
                "base_price_per_night": 150,
                "max_guests": 4,
                "min_nights": 1,
                "max_nights": 5,
                "includes_meals": True,
                "includes_guide": False,
            },
        )

        booking = AdventureBookingModel.objects.create(
            package=package,
            guest_name="AWS Verifier",
            guest_email="aws-verifier@example.com",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=2),
            num_guests=2,
            total_price=300,
            status="CONFIRMED",
        )

        self.stdout.write(self.style.MIGRATE_HEADING("Dispatching AWS side effects..."))

        dynamodb_repository.save_booking_to_dynamodb(booking)
        aws_sqs.send_booking_created_message(booking)
        aws_sns.publish_booking_confirmation(booking)

        self.stdout.write(self.style.SUCCESS(f"Booking {booking.id} processed."))
