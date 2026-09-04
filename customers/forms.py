from django import forms
from bookings.models import Booking, Rating


class BookingForm(forms.ModelForm):
    payment_method = forms.ChoiceField(
        label="Payment method",
        choices=[("upi", "UPI (online)"), ("cash", "Cash to worker")],
        widget=forms.RadioSelect,
        initial="upi",
    )

    class Meta:
        model = Booking
        fields = ["address", "latitude", "longitude", "scheduled_time", "estimated_hours",
                  "notes", "is_emergency"]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 2, "placeholder": "Full service address"}),
            "scheduled_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "latitude": forms.HiddenInput(),
            "longitude": forms.HiddenInput(),
            "notes": forms.Textarea(attrs={"rows": 2, "placeholder": "Describe the issue / job details (optional)"}),
        }


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ["score", "comment"]
        widgets = {
            "score": forms.RadioSelect(choices=[(i, f"{i} ★") for i in range(1, 6)]),
            "comment": forms.Textarea(attrs={"rows": 2, "placeholder": "Share your experience (optional)"}),
        }


class PaymentMethodForm(forms.Form):
    METHOD_CHOICES = [
        ("upi", "UPI"),
        ("card", "Credit/Debit Card"),
        ("wallet", "Wallet"),
        ("cash", "Cash on Service"),
    ]
    method = forms.ChoiceField(choices=METHOD_CHOICES, widget=forms.RadioSelect, initial="upi")
