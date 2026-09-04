from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext as _
from django.http import JsonResponse

from services.models import WorkerProfile
from bookings.models import Booking
from payments.models import Payment
from .forms import WorkerProfileForm, CertificateUploadForm


def worker_required(user):
    return user.is_authenticated and user.is_worker


@login_required
@user_passes_test(worker_required)
def dashboard(request):
    profile, _created = WorkerProfile.objects.get_or_create(user=request.user)
    bookings = Booking.objects.filter(worker=request.user).order_by("-created_at")[:8]
    pending_count = Booking.objects.filter(worker=request.user, status=Booking.Status.PENDING).count()
    active_count = Booking.objects.filter(worker=request.user,
                                           status__in=[Booking.Status.ACCEPTED, Booking.Status.IN_PROGRESS]).count()
    completed_count = Booking.objects.filter(worker=request.user, status=Booking.Status.COMPLETED).count()
    earnings = Payment.objects.filter(booking__worker=request.user, status="success").aggregate(
        total=Sum("worker_payout"))["total"] or 0
    context = {
        "profile": profile,
        "bookings": bookings,
        "pending_count": pending_count,
        "active_count": active_count,
        "completed_count": completed_count,
        "earnings": earnings,
    }
    return render(request, "workers/dashboard.html", context)


@login_required
@user_passes_test(worker_required)
def profile_edit(request):
    profile, _created = WorkerProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = WorkerProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, _("Skill profile updated. Awaiting/maintaining cooperative verification."))
            return redirect("workers:dashboard")
    else:
        form = WorkerProfileForm(instance=profile)
    return render(request, "workers/profile_edit.html", {"form": form, "profile": profile})


@login_required
@user_passes_test(worker_required)
def certificate_upload(request):
    profile, _created = WorkerProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = CertificateUploadForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.is_verified = False
            profile.verification_note = ""
            profile.save()
            messages.success(request, _("Certificate uploaded. Sent for cooperative verification."))
            return redirect("workers:dashboard")
    else:
        form = CertificateUploadForm(instance=profile)
    return render(request, "workers/certificate_upload.html", {"form": form, "profile": profile})


@login_required
@user_passes_test(worker_required)
def toggle_online(request):
    profile, _created = WorkerProfile.objects.get_or_create(user=request.user)
    if not profile.is_verified:
        messages.warning(request, _("You must be verified by the cooperative before going online."))
        return redirect("workers:dashboard")
    profile.is_online = not profile.is_online
    profile.save(update_fields=["is_online"])
    return redirect("workers:dashboard")


@login_required
@user_passes_test(worker_required)
def bookings_list(request):
    status = request.GET.get("status", "")
    qs = Booking.objects.filter(worker=request.user).order_by("-created_at")
    if status:
        qs = qs.filter(status=status)
    return render(request, "workers/bookings_list.html", {"bookings": qs, "status": status,
                                                            "statuses": Booking.Status.choices})


@login_required
@user_passes_test(worker_required)
def booking_action(request, pk, action):
    booking = get_object_or_404(Booking, pk=pk, worker=request.user)
    now = timezone.now()
    if action == "accept" and booking.status == Booking.Status.PENDING:
        booking.status = Booking.Status.ACCEPTED
        booking.accepted_at = now
        booking.save()
        messages.success(request, _("Booking accepted."))
    elif action == "reject" and booking.status == Booking.Status.PENDING:
        booking.status = Booking.Status.REJECTED
        booking.save()
        messages.info(request, _("Booking rejected."))
    elif action == "start" and booking.status == Booking.Status.ACCEPTED:
        booking.status = Booking.Status.IN_PROGRESS
        booking.started_at = now
        booking.save()
        messages.success(request, _("Job marked in progress."))
    elif action == "complete" and booking.status == Booking.Status.IN_PROGRESS:
        booking.status = Booking.Status.COMPLETED
        booking.completed_at = now
        booking.save()
        profile = booking.worker.worker_profile
        profile.jobs_completed += 1
        profile.save(update_fields=["jobs_completed"])
        messages.success(request, _("Job marked complete. Customer can now pay & rate."))
    return redirect("workers:bookings_list")


@login_required
@user_passes_test(worker_required)
def earnings(request):
    payments = Payment.objects.filter(booking__worker=request.user, status="success").order_by("-paid_at")
    total = payments.aggregate(total=Sum("worker_payout"))["total"] or 0
    by_month = {}
    for p in payments:
        key = p.paid_at.strftime("%b %Y") if p.paid_at else "N/A"
        by_month[key] = by_month.get(key, 0) + float(p.worker_payout)
    chart_labels = list(by_month.keys())[::-1]
    chart_values = list(by_month.values())[::-1]
    return render(request, "workers/earnings.html", {
        "payments": payments, "total": total,
        "chart_labels": chart_labels, "chart_values": chart_values,
    })
