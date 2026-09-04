from django.urls import path
from . import views

app_name = "customers"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("services/", views.select_service, name="select_service"),
    path("services/<int:category_id>/workers/", views.find_workers, name="find_workers"),
    path("worker/<int:pk>/", views.worker_profile, name="worker_profile"),
    path("worker/<int:pk>/book/", views.book_worker, name="book_worker"),
    path("bookings/", views.my_bookings, name="my_bookings"),
    path("bookings/<int:pk>/", views.booking_detail, name="booking_detail"),
    path("bookings/<int:pk>/cancel/", views.cancel_booking, name="cancel_booking"),
    path("bookings/<int:pk>/pay/", views.make_payment, name="make_payment"),
    path("bookings/<int:pk>/invoice/", views.invoice, name="invoice"),
    path("bookings/<int:pk>/rate/", views.rate_booking, name="rate_booking"),
    path("emergency/", views.emergency_request, name="emergency"),
]
