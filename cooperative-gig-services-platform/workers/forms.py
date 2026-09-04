from django import forms
from services.models import WorkerProfile, ServiceCategory


class WorkerProfileForm(forms.ModelForm):
    service_categories = forms.ModelMultipleChoiceField(
        queryset=ServiceCategory.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    class Meta:
        model = WorkerProfile
        fields = ["service_categories", "bio", "experience_years", "hourly_rate",
                  "service_area_km", "latitude", "longitude"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 3, "placeholder": "Tell customers about your skills and experience..."}),
            "latitude": forms.HiddenInput(),
            "longitude": forms.HiddenInput(),
        }


class CertificateUploadForm(forms.ModelForm):
    class Meta:
        model = WorkerProfile
        fields = ["certificate_title", "certificate_file"]
