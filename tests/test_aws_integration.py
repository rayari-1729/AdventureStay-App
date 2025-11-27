from datetime import date, timedelta
from unittest import mock

import pytest

from experiences.models import AdventurePackageModel, AdventureBookingModel
from experiences.services import aws_sns, aws_sqs, dynamodb_repository, packages_repository
from experiences.services.aws_s3 import resolve_image_url


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


@mock.patch("experiences.services.packages_repository._should_use_dynamodb", return_value=True)
@mock.patch("experiences.services.packages_repository.dynamodb_repository.list_packages_from_dynamodb")
def test_get_all_packages_reads_from_dynamodb(mock_list, mock_flag):
    expected = [{"package_code": "DYN-1"}]
    mock_list.return_value = expected
    result = packages_repository.get_all_packages()
    assert result == expected
    mock_list.assert_called_once()


@pytest.mark.django_db
def test_get_all_packages_fallbacks_to_db(settings):
    settings.USE_AWS = False
    pkg = AdventurePackageModel.objects.create(
        package_code="LOCAL-1",
        category=AdventurePackageModel.LODGING,
        name="Local Lodge",
        location="Fallback",
        base_price_per_night=99,
        max_guests=4,
        min_nights=1,
        max_nights=3,
        includes_meals=False,
        includes_guide=False,
    )
    packages = packages_repository.get_all_packages()
    assert any(p["package_code"] == pkg.package_code for p in packages)


@mock.patch("experiences.services.packages_repository._should_use_dynamodb", return_value=True)
@mock.patch("experiences.services.packages_repository.dynamodb_repository.get_package_from_dynamodb")
def test_get_package_by_code_dynamodb(mock_get, mock_flag):
    mock_get.return_value = {"package_code": "DYN-2"}
    result = packages_repository.get_package_by_code("DYN-2")
    assert result["package_code"] == "DYN-2"


def test_resolve_image_url_passthrough():
    url = "https://example.com/image.jpg"
    assert resolve_image_url(url) == url


def test_resolve_image_url_for_s3_key(settings):
    settings.S3_BUCKET_NAME = "adventurestay-images"
    settings.AWS_REGION = "ap-south-1"
    result = resolve_image_url("gallery/photo.jpg")
    assert result == "https://adventurestay-images.s3.ap-south-1.amazonaws.com/gallery/photo.jpg"
