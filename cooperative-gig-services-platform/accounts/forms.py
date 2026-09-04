from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class CustomerRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=False)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    address = forms.CharField(max_length=255, required=False)
    preferred_language = forms.ChoiceField(choices=User.Language.choices, initial=User.Language.ENGLISH)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "phone", "address",
                  "preferred_language", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.CUSTOMER
        user.email = self.cleaned_data["email"]
        user.phone = self.cleaned_data["phone"]
        user.address = self.cleaned_data.get("address", "")
        user.preferred_language = self.cleaned_data["preferred_language"]
        if commit:
            user.save()
        return user


class WorkerRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=False)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    address = forms.CharField(max_length=255, required=False)
    preferred_language = forms.ChoiceField(choices=User.Language.choices, initial=User.Language.ENGLISH)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "phone", "address",
                  "preferred_language", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.WORKER
        user.email = self.cleaned_data["email"]
        user.phone = self.cleaned_data["phone"]
        user.address = self.cleaned_data.get("address", "")
        user.preferred_language = self.cleaned_data["preferred_language"]
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "address",
                  "preferred_language", "profile_photo"]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 2}),
        }
