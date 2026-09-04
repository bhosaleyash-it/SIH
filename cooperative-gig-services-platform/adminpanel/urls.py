from django.urls import path
from . import views

app_name = "adminpanel"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("workers/verify/", views.verify_workers, name="verify_workers"),
    path("workers/verify/<int:pk>/", views.verify_worker_detail, name="verify_worker_detail"),
    path("workers/", views.manage_workers, name="manage_workers"),
    path("workers/<int:pk>/toggle-active/", views.toggle_worker_active, name="toggle_worker_active"),
    path("services/", views.manage_services, name="manage_services"),
    path("services/<int:pk>/edit/", views.edit_service, name="edit_service"),
    path("bookings/", views.manage_bookings, name="manage_bookings"),
    path("payments/", views.monitor_payments, name="monitor_payments"),
]
