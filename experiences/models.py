"""Django models for AdventureStay."""

from django.db import models


class AdventurePackageModel(models.Model):
    """Persisted adventure package configuration."""

    TREKKING = "TREKKING"
    HILLS_STAYCATION = "HILLS_STAYCATION"
    JUNGLE_SAFARI = "JUNGLE_SAFARI"
    LODGING = "LODGING"

    CATEGORY_CHOICES = [
        (TREKKING, "Trekking"),
        (HILLS_STAYCATION, "Hills Staycation"),
        (JUNGLE_SAFARI, "Jungle Safari"),
        (LODGING, "Lodging"),
    ]

    package_code = models.CharField(max_length=64, unique=True)
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    base_price_per_night = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    base_price_per_person = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    max_guests = models.PositiveIntegerField()
    min_nights = models.PositiveIntegerField(default=1)
    max_nights = models.PositiveIntegerField(default=7)
    includes_meals = models.BooleanField(default=False)
    includes_guide = models.BooleanField(default=False)
    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.package_code})"


class AdventureBookingModel(models.Model):
    """Stores bookings confirmed via the website."""

    STATUS_CHOICES = [
        ("CONFIRMED", "Confirmed"),
        ("PENDING", "Pending"),
        ("CANCELLED", "Cancelled"),
    ]

    package = models.ForeignKey(
        AdventurePackageModel, on_delete=models.CASCADE, related_name="bookings"
    )
    guest_name = models.CharField(max_length=255, default="")
    guest_email = models.EmailField(default="")
    start_date = models.DateField()
    end_date = models.DateField()
    num_guests = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="CONFIRMED")

    def __str__(self) -> str:
        return (
            f"{self.package.package_code} booking for {self.guest_name} "
            f"({self.start_date} - {self.end_date})"
        )
