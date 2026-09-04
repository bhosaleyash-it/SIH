import uuid
from django.db import models
from django.conf import settings


class Payment(models.Model):
    class Method(models.TextChoices):
        MOCK_CARD = "card", "Credit/Debit Card"
        MOCK_UPI = "upi", "UPI"
        MOCK_WALLET = "wallet", "Wallet"
        CASH = "cash", "Cash on Service"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    booking = models.OneToOneField("bookings.Booking", on_delete=models.CASCADE, related_name="payment")
    transaction_id = models.CharField(max_length=20, unique=True, editable=False, blank=True)
    method = models.CharField(max_length=10, choices=Method.choices, default=Method.MOCK_UPI)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)

    amount = models.DecimalField(max_digits=9, decimal_places=2)
    platform_commission = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    worker_payout = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = "TXN" + uuid.uuid4().hex[:10].upper()
        if not self.platform_commission:
            pct = getattr(settings, "PLATFORM_COMMISSION_PERCENT", 15)
            self.platform_commission = round(self.amount * pct / 100, 2)
            self.worker_payout = self.amount - self.platform_commission
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_id} - {self.amount} ({self.status})"
