from datetime import date, timedelta
from unittest import mock

import pytest

from experiences.models import AdventurePackageModel, AdventureBookingModel
from experiences.services import aws_sns, aws_sqs, dynamodb_repository


@pytest.fixture
def sample_booking(db):
    package = AdventurePackageModel.objects.create(
        package_code="AWS-TST",
        category=AdventurePackageModel.LODGING,
        name="AWS Lodge",
        location="Test Valley",
        base_price_per_night=100,
        max_guests=4,
        min_nights=1,
        max_nights=5,
        includes_meals=True,
        includes_guide=False,
    )
    return AdventureBookingModel.objects.create(
        package=package,
        guest_name="Tester",
        guest_email="tester@example.com",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=2),
        num_guests=2,
        total_price=200,
        status="CONFIRMED",
    )


@mock.patch("experiences.services.dynamodb_repository.boto3.resource")
def test_dynamodb_skips_when_disabled(mock_resource, settings, sample_booking):
    settings.USE_AWS = False
    dynamodb_repository.save_booking_to_dynamodb(sample_booking)
    mock_resource.assert_not_called()


@mock.patch("experiences.services.dynamodb_repository.boto3.resource")
def test_dynamodb_puts_item_when_enabled(mock_resource, settings, sample_booking):
    settings.USE_AWS = True
    settings.DDB_BOOKINGS_TABLE_NAME = "bookings"
    table = mock_resource.return_value.Table.return_value
    dynamodb_repository.save_booking_to_dynamodb(sample_booking)
    table.put_item.assert_called_once()


@mock.patch("experiences.services.aws_sqs.boto3.client")
def test_sqs_sends_message_when_enabled(mock_client, settings, sample_booking):
    settings.USE_AWS = True
    settings.SQS_BOOKING_QUEUE_URL = "https://sqs.mock/queue"
    aws_sqs.send_booking_created_message(sample_booking)
    mock_client.return_value.send_message.assert_called_once()


@mock.patch("experiences.services.aws_sns.boto3.client")
def test_sns_publishes_message_when_enabled(mock_client, settings, sample_booking):
    settings.USE_AWS = True
    settings.SNS_BOOKING_TOPIC_ARN = "arn:aws:sns:region:acct:topic"
    aws_sns.publish_booking_confirmation(sample_booking)
    mock_client.return_value.publish.assert_called_once()
