"""Views powering the AdventureStay site."""

from __future__ import annotations

from decimal import Decimal

from django.shortcuts import get_object_or_404, redirect, render

from adventurestay_utils import build_itinerary_summary

from .forms import BookingForm, to_domain_booking
from .models import AdventureBookingModel, AdventurePackageModel
from .services import aws_enabled
from .services import aws_sqs, aws_sns, dynamodb_repository
from .services.aws_s3 import get_package_image_url


CATEGORY_DESCRIPTIONS = {
    AdventurePackageModel.TREKKING: "Multi-day guided treks with campsite support and alpine thrills.",
    AdventurePackageModel.HILLS_STAYCATION: "Slow down in boutique hill stays with curated meals and bonfires.",
    AdventurePackageModel.JUNGLE_SAFARI: "Immersive wild escapes with certified guides and protected reserve permits.",
    AdventurePackageModel.LODGING: "Rustic homestays and lodges that keep you close to nature and local life.",
}


def home(request):
    return render(
        request,
        "experiences/home.html",
        {
            "title": "AdventureStay",
            "aws_enabled": aws_enabled(),
        },
    )


def package_list(request):
    sections = []
    for key, label in AdventurePackageModel.CATEGORY_CHOICES:
        packages = (
            AdventurePackageModel.objects.filter(category=key, is_active=True)
            .order_by("name")[:5]
        )
        cards = []
        for package in packages:
            price = package.base_price_per_night or package.base_price_per_person or Decimal("0")
            pricing_text = (
                f"From ₹{price} / night" if package.base_price_per_night else f"From ₹{price} / person"
            )
            cards.append(
                {
                    "obj": package,
                    "image": package.image_url or get_package_image_url(package.package_code),
                    "pricing": pricing_text,
                }
            )
        sections.append(
            {
                "key": key.lower(),
                "label": label,
                "description": CATEGORY_DESCRIPTIONS.get(key, ""),
                "packages": cards,
            }
        )

    return render(
        request,
        "experiences/package_list.html",
        {"sections": sections},
    )


def booking_form(request, package_code: str):
    package = get_object_or_404(AdventurePackageModel, package_code=package_code)

    if request.method == "POST":
        form = BookingForm(package, request.POST)
        if form.is_valid():
            booking = AdventureBookingModel.objects.create(
                package=package,
                guest_name=form.cleaned_data["guest_name"],
                guest_email=form.cleaned_data["guest_email"],
                start_date=form.cleaned_data["start_date"],
                end_date=form.cleaned_data["end_date"],
                num_guests=form.cleaned_data["num_guests"],
                total_price=Decimal(str(form.total_price)),
                status="CONFIRMED",
            )
            booking_payload = {
                "booking_id": str(booking.id),
                "package_code": package.package_code,
                "guest_name": booking.guest_name,
                "guest_email": booking.guest_email,
                "start_date": booking.start_date.isoformat(),
                "end_date": booking.end_date.isoformat(),
                "num_guests": booking.num_guests,
                "total_price": float(booking.total_price),
                "itinerary": build_itinerary_summary(to_domain_booking(booking)),
            }
            dynamodb_repository.save_booking_to_dynamodb(booking_payload)
            aws_sqs.send_booking_created_message(booking_payload)
            aws_sns.publish_booking_confirmation(booking_payload)
            return redirect("experiences:booking_success", booking_id=booking.id)
    else:
        form = BookingForm(package)

    return render(
        request,
        "experiences/booking_form.html",
        {
            "package": package,
            "form": form,
            "quote": form.total_price,
        },
    )


def booking_success(request, booking_id: int):
    booking = get_object_or_404(
        AdventureBookingModel.objects.select_related("package"), pk=booking_id
    )
    domain_booking = to_domain_booking(booking)
    itinerary = build_itinerary_summary(domain_booking)
    return render(
        request,
        "experiences/booking_success.html",
        {"booking": booking, "itinerary": itinerary},
    )
