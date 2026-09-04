from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class ServiceCategory(models.Model):
    """A service type e.g. Electrician, Plumber, Carpenter, Cleaner..."""
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, default="bi-tools", help_text="Bootstrap icon class")
    description = models.CharField(max_length=255, blank=True)
    base_rate_per_hour = models.DecimalField(max_digits=8, decimal_places=2, default=200)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Service Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class WorkerProfile(models.Model):
    """Extended profile for users with role=worker."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="worker_profile")
    service_categories = models.ManyToManyField(ServiceCategory, related_name="workers", blank=True)
    bio = models.TextField(blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, default=200)
    certificate_file = models.FileField(upload_to="certificates/", blank=True, null=True)
    certificate_title = models.CharField(max_length=150, blank=True)

    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_note = models.CharField(max_length=255, blank=True)

    is_online = models.BooleanField(default=False)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    service_area_km = models.PositiveIntegerField(default=10)

    rating_avg = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    rating_count = models.PositiveIntegerField(default=0)
    jobs_completed = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Worker: {self.user.get_full_name() or self.user.username}"

    @property
    def status_label(self):
        if not self.is_verified:
            return "Pending Verification"
        return "Online" if self.is_online else "Offline"

    def recalc_rating(self):
        from bookings.models import Rating
        ratings = Rating.objects.filter(booking__worker=self.user)
        count = ratings.count()
        if count:
            avg = sum(r.score for r in ratings) / count
            self.rating_avg = round(avg, 2)
            self.rating_count = count
        else:
            self.rating_avg = 0
            self.rating_count = 0
        self.save(update_fields=["rating_avg", "rating_count"])
