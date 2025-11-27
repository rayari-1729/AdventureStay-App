from unittest import mock

import pytest

from experiences.management.commands.refresh_package_images import Command
from experiences.services import packages_repository
from experiences.services.aws_s3 import resolve_image_url


@mock.patch("experiences.management.commands.refresh_package_images.image_fetcher.fetch_image_for_category")
@mock.patch("experiences.management.commands.refresh_package_images.upload_package_image")
@mock.patch("experiences.services.packages_repository.update_package_image_url")
@mock.patch("experiences.services.dynamodb_repository.list_packages_from_dynamodb")
@mock.patch("experiences.management.commands.refresh_package_images.aws_enabled", return_value=True)
def test_refresh_updates_missing_images(mock_enabled, mock_list, mock_update, mock_upload, mock_fetch, settings):
    mock_list.return_value = [
        {"package_code": "PKG1", "category": "TREKKING", "image_url": ""},
        {"package_code": "PKG2", "category": "LODGING", "image_url": "https://existing"},
    ]
    mock_fetch.return_value = b"image-bytes"
    mock_upload.return_value = "https://bucket/packages/pkg1.jpg"
    settings.S3_BUCKET_NAME = "test-bucket"

    Command().handle()

    mock_fetch.assert_called_once()
    mock_upload.assert_called_once()
    mock_update.assert_called_once_with("PKG1", "https://bucket/packages/pkg1.jpg")


def test_resolve_image_url_handles_https():
    url = "https://example.com/photo.jpg"
    assert resolve_image_url(url) == url
