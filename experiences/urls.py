from django.urls import path

from . import views

app_name = "experiences"

urlpatterns = [
    path("", views.home, name="home"),
    path("packages/", views.package_list, name="package_list"),
    path("packages/<str:package_code>/book/", views.booking_form, name="booking_form"),
    path("bookings/<int:booking_id>/success/", views.booking_success, name="booking_success"),
]
