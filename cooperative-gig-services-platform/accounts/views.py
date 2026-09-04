from django.contrib.auth import login, views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from .forms import CustomerRegisterForm, WorkerRegisterForm, ProfileForm


def register_choice(request):
    return render(request, "accounts/register_choice.html")


def register_customer(request):
    if request.method == "POST":
        form = CustomerRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _("Welcome! Your customer account has been created."))
            return redirect("core:post_login_redirect")
    else:
        form = CustomerRegisterForm()
    return render(request, "accounts/register.html", {"form": form, "role": "Customer"})


def register_worker(request):
    if request.method == "POST":
        form = WorkerRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _("Welcome! Please complete your skill profile to get verified."))
            return redirect("core:post_login_redirect")
    else:
        form = WorkerRegisterForm()
    return render(request, "accounts/register.html", {"form": form, "role": "Worker"})


class CoopLoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _("Profile updated."))
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=request.user)
    return render(request, "accounts/profile.html", {"form": form})
