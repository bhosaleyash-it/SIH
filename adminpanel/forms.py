from django import forms
from services.models import ServiceCategory


class ServiceCategoryForm(forms.ModelForm):
    class Meta:
        model = ServiceCategory
        fields = ["name", "icon", "description", "base_rate_per_hour", "is_active"]


class VerifyWorkerForm(forms.Form):
    decision = forms.ChoiceField(choices=[("approve", "Approve"), ("reject", "Reject")], widget=forms.RadioSelect)
    note = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}))
