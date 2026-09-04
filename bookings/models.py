import uuid 
from decimal import Decimal 
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending Confirmation"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    booking_ref = models.CharField(max_length=12, unique=True, editable=False, blank=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings_made")
    worker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings_received")
    service_category = models.ForeignKey("services.ServiceCategory", on_delete=models.PROTECT, related_name="bookings")

    address = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    distance_km = models.FloatField(null=True, blank=True)

    scheduled_time = models.DateTimeField()
    notes = models.TextField(blank=True)
    is_emergency = models.BooleanField(default=False)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    estimated_hours = models.DecimalField(max_digits=4, decimal_places=1, default=1)
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.booking_ref:
            self.booking_ref = "CG" + uuid.uuid4().hex[:8].upper()
        if not self.price:
            rate = self.service_category.base_rate_per_hour
            try:
                rate = self.worker.worker_profile.hourly_rate
            except Exception:
                pass
            self.price = rate * Decimal(str(self.estimated_hours))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.booking_ref} - {self.service_category} for {self.customer}"

    @property
    def status_badge(self):
        mapping = {
            self.Status.PENDING: "warning",
            self.Status.ACCEPTED: "info",
            self.Status.REJECTED: "danger",
            self.Status.IN_PROGRESS: "primary",
            self.Status.COMPLETED: "success",
            self.Status.CANCELLED: "secondary",
        }
        return mapping.get(self.status, "secondary")

    @property
    def progress_percent(self):
        mapping = {
            self.Status.PENDING: 15,
            self.Status.ACCEPTED: 40,
            self.Status.IN_PROGRESS: 70,
            self.Status.COMPLETED: 100,
            self.Status.REJECTED: 100,
            self.Status.CANCELLED: 100,
        }
        return mapping.get(self.status, 0)

    @property
    def is_paid(self):
        return hasattr(self, "payment") and self.payment.status == "success"


class Rating(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="rating")
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ratings_given")
    score = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.score}★ for {self.booking.worker} ({self.booking.booking_ref})"
