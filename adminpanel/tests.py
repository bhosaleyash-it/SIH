from decimal import Decimal

from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TestCase, RequestFactory
from django.utils import timezone

from accounts.models import User
from adminpanel.views import normalize_money
from bookings.models import Booking
from payments.models import Payment
from services.models import ServiceCategory, WorkerProfile
from workers.views import booking_action


class NormalizeMoneyTests(TestCase):
    def test_normalize_money_rounds_to_two_decimals(self):
        self.assertEqual(normalize_money(Decimal("4377.20000000000")), Decimal("4377.20"))
        self.assertEqual(normalize_money(Decimal("656.570000000000")), Decimal("656.57"))
        self.assertEqual(normalize_money(None), Decimal("0.00"))


class BookingPaymentFlowTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.customer = User.objects.create_user(
            username="customer_cash_test", first_name="Customer", last_name="Test",
            role=User.Role.CUSTOMER, phone="9999999999"
        )
        self.worker_user = User.objects.create_user(
            username="worker_cash_test", first_name="Worker", last_name="Test",
            role=User.Role.WORKER, phone="8888888888"
        )
        self.category = ServiceCategory.objects.create(name="Technician", base_rate_per_hour=Decimal("250.00"))
        self.profile = WorkerProfile.objects.create(
            user=self.worker_user,
            is_verified=True,
            is_online=True,
            hourly_rate=Decimal("250.00"),
        )
        self.profile.service_categories.add(self.category)

    def test_complete_booking_creates_cash_payment_record(self):
        booking = Booking.objects.create(
            customer=self.customer,
            worker=self.worker_user,
            service_category=self.category,
            address="Test address",
            scheduled_time=timezone.now(),
            estimated_hours=Decimal("2.0"),
            status=Booking.Status.IN_PROGRESS,
        )

        request = self.factory.post(f"/workers/bookings/{booking.pk}/complete/")
        request.user = self.worker_user
        setattr(request, "session", {})
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        response = booking_action(request, booking.pk, "complete")
        booking.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(booking.status, Booking.Status.COMPLETED)
        payment = Payment.objects.get(booking=booking)
        self.assertEqual(payment.method, Payment.Method.CASH)
        self.assertEqual(payment.status, Payment.Status.SUCCESS)
        self.assertEqual(payment.amount, booking.price)
