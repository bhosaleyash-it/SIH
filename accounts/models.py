from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user with role-based access for Customer / Worker / Admin (cooperative)."""

    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        WORKER = "worker", "Worker"
        ADMIN = "admin", "Cooperative Admin"

    class Language(models.TextChoices):
        ENGLISH = "en", "English"
        HINDI = "hi", "हिन्दी"
        GUJARATI = "gu", "ગુજરાતી"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.CUSTOMER)
    phone = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=255, blank=True)
    preferred_language = models.CharField(max_length=5, choices=Language.choices, default=Language.ENGLISH)
    profile_photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_customer(self):
        return self.role == self.Role.CUSTOMER

    @property
    def is_worker(self):
        return self.role == self.Role.WORKER

    @property
    def is_coop_admin(self):
        return self.role == self.Role.ADMIN
