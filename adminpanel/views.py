from decimal import Decimal

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, Avg
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext as _
from datetime import timedelta

from accounts.models import User
from services.models import ServiceCategory, WorkerProfile
from bookings.models import Booking, Rating
from payments.models import Payment
from .forms import ServiceCategoryForm, VerifyWorkerForm


def admin_required(user):
    return user.is_authenticated and user.is_coop_admin


def normalize_money(value):
    if value in (None, ""):
        return Decimal("0.00")
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")


@login_required
@user_passes_test(admin_required)
def dashboard(request):
    total_customers = User.objects.filter(role=User.Role.CUSTOMER).count()
    total_workers = User.objects.filter(role=User.Role.WORKER).count()
    verified_workers = WorkerProfile.objects.filter(is_verified=True).count()
    pending_verifications = WorkerProfile.objects.filter(is_verified=False).exclude(certificate_file="").count()
    total_bookings = Booking.objects.count()
    active_bookings = Booking.objects.filter(
        status__in=[Booking.Status.PENDING, Booking.Status.ACCEPTED, Booking.Status.IN_PROGRESS]).count()
    completed_bookings = Booking.objects.filter(status=Booking.Status.COMPLETED).count()

    revenue = Payment.objects.filter(status="success").aggregate(
        total=Sum("amount"), commission=Sum("platform_commission"))
    total_revenue = normalize_money(revenue["total"])
    total_commission = normalize_money(revenue["commission"])

    # Bookings by category for chart
    cat_data = (Booking.objects.values("service_category__name")
                .annotate(count=Count("id")).order_by("-count")[:8])
    cat_labels = [c["service_category__name"] for c in cat_data]
    cat_counts = [c["count"] for c in cat_data]

    # Revenue trend bucketed by month
    buckets = {}
    for p in Payment.objects.filter(status="success"):
        if p.paid_at:
            key = p.paid_at.strftime("%b %Y")
            buckets[key] = buckets.get(key, 0) + float(p.amount)
    months = list(buckets.keys())
    month_revenue = list(buckets.values())

    status_data = Booking.objects.values("status").annotate(count=Count("id"))
    status_labels = [dict(Booking.Status.choices).get(s["status"], s["status"]) for s in status_data]
    status_counts = [s["count"] for s in status_data]

    context = {
        "total_customers": total_customers,
        "total_workers": total_workers,
        "verified_workers": verified_workers,
        "pending_verifications": pending_verifications,
        "total_bookings": total_bookings,
        "active_bookings": active_bookings,
        "completed_bookings": completed_bookings,
        "total_revenue": total_revenue,
        "total_commission": total_commission,
        "cat_labels": cat_labels,
        "cat_counts": cat_counts,
        "months": months,
        "month_revenue": month_revenue,
        "status_labels": status_labels,
        "status_counts": status_counts,
    }
    return render(request, "adminpanel/dashboard.html", context)


@login_required
@user_passes_test(admin_required)
def verify_workers(request):
    pending = WorkerProfile.objects.filter(is_verified=False).select_related("user").order_by("-created_at")
    verified = WorkerProfile.objects.filter(is_verified=True).select_related("user").order_by("-verified_at")[:10]
    return render(request, "adminpanel/verify_workers.html", {"pending": pending, "verified": verified})


@login_required
@user_passes_test(admin_required)
def verify_worker_detail(request, pk):
    profile = get_object_or_404(WorkerProfile.objects.select_related("user"), pk=pk)
    if request.method == "POST":
        form = VerifyWorkerForm(request.POST)
        if form.is_valid():
            decision = form.cleaned_data["decision"]
            profile.verification_note = form.cleaned_data["note"]
            if decision == "approve":
                profile.is_verified = True
                profile.verified_at = timezone.now()
                messages.success(request, _("Worker verified successfully."))
            else:
                profile.is_verified = False
                messages.info(request, _("Worker verification rejected."))
            profile.save()
            return redirect("adminpanel:verify_workers")
    else:
        form = VerifyWorkerForm()
    return render(request, "adminpanel/verify_worker_detail.html", {"profile": profile, "form": form})


@login_required
@user_passes_test(admin_required)
def manage_workers(request):
    workers = WorkerProfile.objects.select_related("user").order_by("-created_at")
    return render(request, "adminpanel/manage_workers.html", {"workers": workers})


@login_required
@user_passes_test(admin_required)
def toggle_worker_active(request, pk):
    profile = get_object_or_404(WorkerProfile, pk=pk)
    profile.user.is_active = not profile.user.is_active
    profile.user.save(update_fields=["is_active"])
    messages.success(request, _("Worker account status updated."))
    return redirect("adminpanel:manage_workers")


@login_required
@user_passes_test(admin_required)
def manage_services(request):
    services = ServiceCategory.objects.all()
    if request.method == "POST":
        form = ServiceCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Service category added."))
            return redirect("adminpanel:manage_services")
    else:
        form = ServiceCategoryForm()
    return render(request, "adminpanel/manage_services.html", {"services": services, "form": form})


@login_required
@user_passes_test(admin_required)
def edit_service(request, pk):
    service = get_object_or_404(ServiceCategory, pk=pk)
    if request.method == "POST":
        form = ServiceCategoryForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, _("Service updated."))
            return redirect("adminpanel:manage_services")
    else:
        form = ServiceCategoryForm(instance=service)
    return render(request, "adminpanel/edit_service.html", {"form": form, "service": service})


@login_required
@user_passes_test(admin_required)
def manage_bookings(request):
    status = request.GET.get("status", "")
    qs = Booking.objects.select_related("customer", "worker", "service_category").order_by("-created_at")
    if status:
        qs = qs.filter(status=status)
    return render(request, "adminpanel/manage_bookings.html", {"bookings": qs, "status": status,
                                                                 "statuses": Booking.Status.choices})


@login_required
@user_passes_test(admin_required)
def monitor_payments(request):
    payments = Payment.objects.select_related("booking").order_by("-created_at")
    successful = payments.filter(status="success")
    totals = successful.aggregate(
        total=Sum("amount"), commission=Sum("platform_commission"), payout=Sum("worker_payout"))
    totals["online_total"] = successful.filter(method__in=[Payment.Method.MOCK_UPI, Payment.Method.MOCK_CARD, Payment.Method.MOCK_WALLET])\
        .aggregate(total=Sum("amount"))["total"] or 0
    totals["cash_total"] = successful.filter(method=Payment.Method.CASH).aggregate(total=Sum("amount"))["total"] or 0
    return render(request, "adminpanel/monitor_payments.html", {"payments": payments, "totals": totals})


@login_required
@user_passes_test(admin_required)
def approve_cash_payment(request, pk):
    payment = get_object_or_404(Payment, pk=pk, method=Payment.Method.CASH)
    if request.method == "POST" and payment.status != Payment.Status.SUCCESS and payment.worker_confirmed_at:
        payment.status = Payment.Status.SUCCESS
        payment.paid_at = timezone.now()
        payment.admin_approved_at = payment.paid_at
        payment.admin_approved_by = request.user
        payment.save(update_fields=["status", "paid_at", "admin_approved_at", "admin_approved_by"])
        messages.success(request, _("Cash payment approved."))
    return redirect("adminpanel:monitor_payments")
