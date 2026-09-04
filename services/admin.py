from django.contrib import admin
from .models import ServiceCategory, WorkerProfile


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "base_rate_per_hour", "is_active")
    list_filter = ("is_active",)


@admin.register(WorkerProfile)
class WorkerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "is_verified", "is_online", "rating_avg", "jobs_completed")
    list_filter = ("is_verified", "is_online")
