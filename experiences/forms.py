"""Forms powering the booking flow."""

from __future__ import annotations

from django import forms

from adventurestay_utils import (
    AdventureBooking,
    AdventurePackage,
    AdventurePriceCalculator,
    PackageAvailabilityChecker,
    PackageBookingValidator,
    InvalidDateRangeError,
    InvalidGuestCountError,
    PackageNotAvailableError,
)

from .models import AdventureBookingModel, AdventurePackageModel


def to_domain_package(package_model: AdventurePackageModel) -> AdventurePackage:
    """Convert a Django model instance into the pure domain dataclass."""

    return AdventurePackage(
        package_id=package_model.package_code,
        category=package_model.category,
        name=package_model.name,
        location=package_model.location,
        base_price_per_night=float(package_model.base_price_per_night)
        if package_model.base_price_per_night is not None
        else None,
        base_price_per_person=float(package_model.base_price_per_person)
        if package_model.base_price_per_person is not None
        else None,
        max_guests=package_model.max_guests,
        min_nights=package_model.min_nights,
        max_nights=package_model.max_nights,
        includes_meals=package_model.includes_meals,
        includes_guide=package_model.includes_guide,
        is_active=package_model.is_active,
    )


def to_domain_booking(booking_model: AdventureBookingModel) -> AdventureBooking:
    package = to_domain_package(booking_model.package)
    nights = (booking_model.end_date - booking_model.start_date).days
    return AdventureBooking(
        package=package,
        start_date=booking_model.start_date,
        end_date=booking_model.end_date,
        num_guests=booking_model.num_guests,
        nights=nights,
        total_price=float(booking_model.total_price),
    )


class BookingForm(forms.Form):
    """Validates guest info plus date and guest selections for a package."""

    guest_name = forms.CharField(
        max_length=255, label="Guest Name", widget=forms.TextInput(attrs={"placeholder": "Aditi Rao"})
    )
    guest_email = forms.EmailField(
        label="Email", widget=forms.EmailInput(attrs={"placeholder": "guest@example.com"})
    )
    start_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    num_guests = forms.IntegerField(min_value=1, label="Number of Guests")

    def __init__(
        self,
        package: AdventurePackageModel,
        *args,
        availability_checker: PackageAvailabilityChecker | None = None,
        price_calculator: AdventurePriceCalculator | None = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.package = package
        self.availability_checker = availability_checker or PackageAvailabilityChecker()
        self.price_calculator = price_calculator or AdventurePriceCalculator()
        self._booking_request = None
        self._total_price = None
        self._customer_details = None

    def clean(self):
        cleaned_data = super().clean()
        if self.errors:
            return cleaned_data

        package = to_domain_package(self.package)
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        num_guests = cleaned_data.get("num_guests")

        if not all([start_date, end_date, num_guests]):
            return cleaned_data

        try:
            booking_request = PackageBookingValidator.create_booking_request(
                package, start_date, end_date, num_guests
            )
            existing = [to_domain_booking(b) for b in self.package.bookings.all()]
            self.availability_checker.check_availability(
                booking_request, package, existing
            )
            total_price = self.price_calculator.calculate_price(booking_request, package)
        except (InvalidDateRangeError, InvalidGuestCountError) as exc:
            raise forms.ValidationError(str(exc)) from exc
        except PackageNotAvailableError as exc:
            raise forms.ValidationError(str(exc)) from exc

        self._booking_request = booking_request
        self._total_price = total_price
        self._customer_details = {
            "guest_name": cleaned_data["guest_name"],
            "guest_email": cleaned_data["guest_email"],
        }
        return cleaned_data

    @property
    def booking_request(self):
        return self._booking_request

    @property
    def total_price(self):
        return self._total_price

    @property
    def customer_details(self):
        return self._customer_details
