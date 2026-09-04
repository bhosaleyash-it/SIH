from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register_choice, name="register_choice"),
    path("register/customer/", views.register_customer, name="register_customer"),
    path("register/worker/", views.register_worker, name="register_worker"),
    path("login/", views.CoopLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("profile/", views.profile, name="profile"),
]
