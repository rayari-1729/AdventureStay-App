from django.contrib import admin

from .models import AdventureBookingModel, AdventurePackageModel


@admin.register(AdventurePackageModel)
class AdventurePackageAdmin(admin.ModelAdmin):
    list_display = ("package_code", "name", "category", "location", "is_active")
    search_fields = ("package_code", "name", "location")
    list_filter = ("category", "is_active")


@admin.register(AdventureBookingModel)
class AdventureBookingAdmin(admin.ModelAdmin):
    list_display = (
        "package",
        "guest_name",
        "guest_email",
        "start_date",
        "end_date",
        "num_guests",
        "status",
    )
    list_filter = ("status", "package__category")
    search_fields = ("package__package_code",)
