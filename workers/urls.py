from django.urls import path
from . import views

app_name = "workers"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("certificate/upload/", views.certificate_upload, name="certificate_upload"),
    path("toggle-online/", views.toggle_online, name="toggle_online"),
    path("bookings/", views.bookings_list, name="bookings_list"),
    path("bookings/<int:pk>/<str:action>/", views.booking_action, name="booking_action"),
    path("earnings/", views.earnings, name="earnings"),
]
