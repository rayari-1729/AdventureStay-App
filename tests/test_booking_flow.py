import pytest
from django.urls import reverse

from experiences.models import AdventurePackageModel, AdventureBookingModel


@pytest.mark.django_db
def test_booking_flow_creates_record(client, monkeypatch):
    package = AdventurePackageModel.objects.create(
        package_code="PKG100",
        category=AdventurePackageModel.LODGING,
        name="Mountain Cabin",
        location="Mussoorie",
        base_price_per_night=120,
        max_guests=4,
        min_nights=1,
        max_nights=5,
        includes_meals=True,
        includes_guide=False,
        is_active=True,
    )

    for path in [
        "experiences.services.dynamodb_repository.save_booking_to_dynamodb",
        "experiences.services.aws_sqs.send_booking_created_message",
        "experiences.services.aws_sns.publish_booking_confirmation",
    ]:
        monkeypatch.setattr(path, lambda *args, **kwargs: None)

    response = client.post(
        reverse("experiences:booking_form", args=[package.package_code]),
        {
            "guest_name": "Test Guest",
            "guest_email": "guest@example.com",
            "start_date": "2025-06-01",
            "end_date": "2025-06-03",
            "num_guests": 2,
        },
    )

    assert response.status_code == 302
    assert AdventureBookingModel.objects.count() == 1
    booking = AdventureBookingModel.objects.first()
    assert booking.total_price > 0
