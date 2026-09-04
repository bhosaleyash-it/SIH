from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from services.models import ServiceCategory, WorkerProfile
from bookings.models import Booking


def home(request):
    categories = ServiceCategory.objects.filter(is_active=True)
    stats = {
        "workers": WorkerProfile.objects.filter(is_verified=True).count(),
        "bookings": Booking.objects.count(),
        "categories": categories.count(),
    }
    return render(request, "core/home.html", {"categories": categories, "stats": stats})


@login_required
def post_login_redirect(request):
    user = request.user
    if user.is_worker:
        return redirect("workers:dashboard")
    if user.is_coop_admin:
        return redirect("adminpanel:dashboard")
    return redirect("customers:dashboard")


def about(request):
    return render(request, "core/about.html")
