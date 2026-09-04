import random
from decimal import Decimal
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext as _
from django.urls import reverse

from services.models import ServiceCategory, WorkerProfile
from bookings.models import Booking, Rating
from payments.models import Payment
from core.utils import haversine_km
from .forms import BookingForm, RatingForm, PaymentMethodForm


def customer_required(user):
    return user.is_authenticated and user.is_customer


@login_required
@user_passes_test(customer_required)
def dashboard(request):
    categories = ServiceCategory.objects.filter(is_active=True)
    bookings = Booking.objects.filter(customer=request.user).order_by("-created_at")[:6]
    active = Booking.objects.filter(customer=request.user,
                                     status__in=[Booking.Status.PENDING, Booking.Status.ACCEPTED,
                                                 Booking.Status.IN_PROGRESS]).count()
    completed = Booking.objects.filter(customer=request.user, status=Booking.Status.COMPLETED).count()
    return render(request, "customers/dashboard.html", {
        "categories": categories, "bookings": bookings, "active": active, "completed": completed,
    })


@login_required
@user_passes_test(customer_required)
def select_service(request):
    categories = ServiceCategory.objects.filter(is_active=True)
    return render(request, "customers/select_service.html", {"categories": categories})


@login_required
@user_passes_test(customer_required)
def find_workers(request, category_id):
    category = get_object_or_404(ServiceCategory, pk=category_id)
    lat = request.GET.get("lat")
    lng = request.GET.get("lng")
    emergency = request.GET.get("emergency") == "1"

    try:
        lat = float(lat) if lat else (request.user.latitude or 23.0225)
        lng = float(lng) if lng else (request.user.longitude or 72.5714)
    except (TypeError, ValueError):
        lat, lng = 23.0225, 72.5714  # Ahmedabad default

    qs = WorkerProfile.objects.filter(service_categories=category, is_verified=True)
    if emergency:
        qs = qs.filter(is_online=True)

    workers = []
    for w in qs.select_related("user"):
        dist = haversine_km(lat, lng, w.latitude, w.longitude) if w.latitude else None
        workers.append((dist if dist is not None else 9999, w))
    workers.sort(key=lambda t: t[0])
    workers = [(d, w) for d, w in workers if True]

    return render(request, "customers/find_workers.html", {
        "category": category, "workers": workers, "lat": lat, "lng": lng, "emergency": emergency,
    })


@login_required
@user_passes_test(customer_required)
def worker_profile(request, pk):
    profile = get_object_or_404(WorkerProfile.objects.select_related("user"), pk=pk)
    reviews = Rating.objects.filter(booking__worker=profile.user).order_by("-created_at")[:10]
    return render(request, "customers/worker_profile.html", {"profile": profile, "reviews": reviews})


@login_required
@user_passes_test(customer_required)
def book_worker(request, pk):
    profile = get_object_or_404(WorkerProfile.objects.select_related("user"), pk=pk)
    category = profile.service_categories.first()
    is_emergency = request.GET.get("emergency") == "1"
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.customer = request.user
            booking.worker = profile.user
            booking.service_category = category
            if booking.latitude and profile.latitude:
                booking.distance_km = haversine_km(booking.latitude, booking.longitude,
                                                     profile.latitude, profile.longitude)
            booking.save()
            messages.success(request, _("Booking request sent! Track its status below."))
            return redirect("customers:booking_detail", pk=booking.pk)
    else:
        initial = {"is_emergency": is_emergency, "address": request.user.address}
        if is_emergency:
            initial["scheduled_time"] = timezone.now().strftime("%Y-%m-%dT%H:%M")
        form = BookingForm(initial=initial)
    return render(request, "customers/book_worker.html", {"form": form, "profile": profile,
                                                            "is_emergency": is_emergency})


@login_required
@user_passes_test(customer_required)
def my_bookings(request):
    status = request.GET.get("status", "")
    qs = Booking.objects.filter(customer=request.user).order_by("-created_at")
    if status:
        qs = qs.filter(status=status)
    return render(request, "customers/my_bookings.html", {"bookings": qs, "status": status,
                                                            "statuses": Booking.Status.choices})


@login_required
@user_passes_test(customer_required)
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk, customer=request.user)
    return render(request, "customers/booking_detail.html", {"booking": booking})


@login_required
@user_passes_test(customer_required)
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, customer=request.user)
    if booking.status in [Booking.Status.PENDING, Booking.Status.ACCEPTED]:
        booking.status = Booking.Status.CANCELLED
        booking.save()
        messages.info(request, _("Booking cancelled."))
    return redirect("customers:booking_detail", pk=pk)


@login_required
@user_passes_test(customer_required)
def make_payment(request, pk):
    booking = get_object_or_404(Booking, pk=pk, customer=request.user)
    if booking.status != Booking.Status.COMPLETED:
        messages.warning(request, _("Payment is available once the job is completed."))
        return redirect("customers:booking_detail", pk=pk)
    payment, _created = Payment.objects.get_or_create(booking=booking, defaults={"amount": booking.price})
    if payment.status == Payment.Status.SUCCESS:
        return redirect("customers:invoice", pk=pk)

    if request.method == "POST":
        form = PaymentMethodForm(request.POST)
        if form.is_valid():
            payment.method = form.cleaned_data["method"]
            payment.status = Payment.Status.SUCCESS  # mock gateway: always succeeds
            payment.paid_at = timezone.now()
            payment.save()
            messages.success(request, _("Payment successful! Your invoice is ready."))
            return redirect("customers:invoice", pk=pk)
    else:
        form = PaymentMethodForm()
    return render(request, "customers/payment.html", {"form": form, "booking": booking, "payment": payment})


@login_required
@user_passes_test(customer_required)
def invoice(request, pk):
    booking = get_object_or_404(Booking, pk=pk, customer=request.user)
    payment = getattr(booking, "payment", None)
    return render(request, "customers/invoice.html", {"booking": booking, "payment": payment})


@login_required
@user_passes_test(customer_required)
def rate_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, customer=request.user)
    if booking.status != Booking.Status.COMPLETED:
        messages.warning(request, _("You can rate a job after it is completed."))
        return redirect("customers:booking_detail", pk=pk)
    if hasattr(booking, "rating"):
        messages.info(request, _("You already rated this booking."))
        return redirect("customers:booking_detail", pk=pk)
    if request.method == "POST":
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.booking = booking
            rating.customer = request.user
            rating.save()
            profile = booking.worker.worker_profile
            profile.recalc_rating()
            messages.success(request, _("Thanks for your feedback!"))
            return redirect("customers:booking_detail", pk=pk)
    else:
        form = RatingForm()
    return render(request, "customers/rate_booking.html", {"form": form, "booking": booking})


@login_required
@user_passes_test(customer_required)
def emergency_request(request):
    categories = ServiceCategory.objects.filter(is_active=True)
    return render(request, "customers/emergency.html", {"categories": categories})
