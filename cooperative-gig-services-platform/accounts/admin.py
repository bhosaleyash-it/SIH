from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CoopUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "phone", "is_active", "created_at")
    list_filter = ("role", "is_active", "preferred_language")
    fieldsets = UserAdmin.fieldsets + (
        ("Cooperative Info", {"fields": ("role", "phone", "address", "preferred_language",
                                          "profile_photo", "latitude", "longitude")}),
    )
