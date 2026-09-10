import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User
from services.models import ServiceCategory, WorkerProfile
from bookings.models import Booking, Rating
from payments.models import Payment


# Ahmedabad-area coordinates for realistic demo locations
CENTER_LAT, CENTER_LNG = 23.0225, 72.5714


def jitter(base, spread=0.09):
    return round(base + random.uniform(-spread, spread), 6)


class Command(BaseCommand):
    help = "Seed the database with realistic sample data for the Cooperative Gig Services Platform"

    def add_arguments(self, parser):
        parser.add_argument("--flush", action="store_true", help="Delete existing demo data before seeding")

    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write("Clearing existing data...")
            Rating.objects.all().delete()
            Payment.objects.all().delete()
            Booking.objects.all().delete()
            WorkerProfile.objects.all().delete()
            User.objects.exclude(is_superuser=True).delete()

        self.stdout.write("Creating cooperative admin...")
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults=dict(
                email="admin@coopgig.example",
                first_name="Cooperative",
                last_name="Admin",
                role=User.Role.ADMIN,
                phone="9820000001",
                is_staff=True,
                is_superuser=True,
            ),
        )
        if created:
            admin.set_password("coopadmin123")
            admin.save()

        self.stdout.write("Creating service categories...")
        categories_data = [
            ("AC Technician", "bi-snow", "Cooling system repair, installation and servicing", 350),
            ("Electrician", "bi-lightning-charge", "Wiring, repairs, installations", 250),
            ("Plumber", "bi-droplet", "Pipe fitting, leak repair, fixtures", 220),
            ("Carpenter", "bi-hammer", "Furniture, doors, woodwork", 240),
            ("Cleaner", "bi-bucket", "Home & office deep cleaning", 180),
            ("Painter", "bi-brush", "Interior & exterior painting", 200),
            ("Gardener", "bi-flower1", "Lawn care, landscaping, pruning", 160),
            ("Driver", "bi-truck", "Local driving & delivery services", 190),
            ("Caregiver", "bi-heart-pulse", "Home care and elder support", 210),
            ("Technician", "bi-cpu", "Appliance & electronics repair", 260),
            ("Solar Technician", "bi-sun", "Solar pump and panel maintenance", 300),
            ("Pump Technician", "bi-water", "Water and borewell pump service", 280),
            ("Agricultural Technician", "bi-tractor", "Farm equipment repair", 320),
            ("Irrigation pump repair", "bi-water", "Rural irrigation support", 280),
            ("Solar pump maintenance", "bi-sun", "Solar pump preventive upkeep", 300),
            ("School maintenance", "bi-building", "Institution upkeep support", 260),
            ("Community water pump", "bi-droplet-half", "Community water infrastructure", 240),
        ]
        categories = {}
        for name, icon, desc, rate in categories_data:
            cat, _ = ServiceCategory.objects.get_or_create(
                name=name, defaults=dict(icon=icon, description=desc, base_rate_per_hour=rate)
            )
            categories[name] = cat

        self.stdout.write("Creating sample customers...")
        customers_data = [
            ("priya_customer", "Priya", "Sharma", "9825011001"),
            ("amit_customer", "Amit", "Patel", "9825011002"),
            ("sneha_customer", "Sneha", "Mehta", "9825011003"),
            ("rahul_customer", "Rahul", "Joshi", "9825011004"),
        ]
        customers = []
        for username, fn, ln, phone in customers_data:
            u, created = User.objects.get_or_create(
                username=username,
                defaults=dict(
                    email=f"{username}@example.com", first_name=fn, last_name=ln,
                    role=User.Role.CUSTOMER, phone=phone,
                    address=f"{random.randint(1,200)} Satellite Road, Ahmedabad",
                    latitude=jitter(CENTER_LAT, 0.05), longitude=jitter(CENTER_LNG, 0.05),
                ),
            )
            if created:
                u.set_password("customer@123")
                u.save()
            customers.append(u)

        self.stdout.write("Creating sample workers...")
        workers_data = [
            ("rakesh_electrician", "Rakesh", "Vora", "Electrician", 8, True, True, "Certified electrician with residential & commercial wiring experience."),
            ("suresh_plumber", "Suresh", "Thakor", "Plumber", 6, True, True, "Expert in leak repair, bathroom fittings, and pipeline installation."),
            ("manoj_carpenter", "Manoj", "Solanki", "Carpenter", 10, True, False, "Custom furniture, modular kitchens, and door/window carpentry."),
            ("geeta_cleaner", "Geeta", "Bhatt", "Cleaner", 4, True, True, "Deep cleaning specialist for homes and offices, eco-friendly products."),
            ("kiran_painter", "Kiran", "Rana", "Painter", 7, True, True, "Interior & exterior painting, texture work, waterproofing."),
            ("dilip_gardener", "Dilip", "Chauhan", "Gardener", 5, True, False, "Lawn maintenance, landscaping design, and plant care."),
            ("hitesh_driver", "Hitesh", "Parmar", "Driver", 9, True, True, "Safe local driving, outstation trips, and delivery services."),
            ("nilesh_technician", "Nilesh", "Shah", "Technician", 6, True, True, "AC, refrigerator, washing machine repair specialist."),
            ("vijay_electrician", "Vijay", "Desai", "Electrician", 3, False, False, "New to the cooperative — pending certificate verification."),
            ("ramesh_plumber", "Ramesh", "Trivedi", "Plumber", 12, True, False, "Senior plumber, 12+ years across Ahmedabad."),
        ]
        workers = []
        for username, fn, ln, cat_name, exp, verified, online, bio in workers_data:
            u, created = User.objects.get_or_create(
                username=username,
                defaults=dict(
                    email=f"{username}@example.com", first_name=fn, last_name=ln,
                    role=User.Role.WORKER, phone=f"98250{random.randint(20000,29999)}",
                    address=f"{random.randint(1,200)} Cooperative Nagar, Ahmedabad",
                ),
            )
            if created:
                u.set_password("worker@123")
                u.save()
            profile, _ = WorkerProfile.objects.get_or_create(
                user=u,
                defaults=dict(
                    bio=bio, experience_years=exp,
                    hourly_rate=categories[cat_name].base_rate_per_hour + random.randint(-20, 40),
                    is_verified=verified, is_online=online,
                    verified_at=timezone.now() - timedelta(days=random.randint(1, 60)) if verified else None,
                    latitude=jitter(CENTER_LAT), longitude=jitter(CENTER_LNG),
                    service_area_km=random.choice([8, 10, 15]),
                    jobs_completed=random.randint(5, 60) if verified else 0,
                ),
            )
            profile.service_categories.add(categories[cat_name])
            if not verified:
                profile.certificate_title = ""
            else:
                profile.certificate_title = f"{cat_name} Trade Certificate"
            profile.save()
            workers.append(profile)

        self.stdout.write("Creating sample bookings, payments & ratings...")
        statuses_cycle = [Booking.Status.COMPLETED, Booking.Status.COMPLETED, Booking.Status.COMPLETED,
                           Booking.Status.IN_PROGRESS, Booking.Status.ACCEPTED, Booking.Status.PENDING,
                           Booking.Status.CANCELLED]
        verified_workers = [w for w in workers if w.is_verified]
        booking_count = 0
        for i in range(28):
            customer = random.choice(customers)
            worker_profile = random.choice(verified_workers)
            category = worker_profile.service_categories.first()
            status = random.choice(statuses_cycle)
            days_ago = random.randint(0, 45)
            scheduled = timezone.now() - timedelta(days=days_ago, hours=random.randint(-5, 5))
            hours = random.choice([1, 1.5, 2, 3])

            booking = Booking(
                customer=customer, worker=worker_profile.user, service_category=category,
                address=customer.address or "Ahmedabad", latitude=jitter(CENTER_LAT), longitude=jitter(CENTER_LNG),
                scheduled_time=scheduled, estimated_hours=hours,
                notes=random.choice(["", "Please call before arriving.", "Urgent repair needed.", "Second floor flat."]),
                is_emergency=random.random() < 0.15,
                status=status,
            )
            if status in [Booking.Status.ACCEPTED, Booking.Status.IN_PROGRESS, Booking.Status.COMPLETED]:
                booking.accepted_at = scheduled - timedelta(hours=1)
            if status in [Booking.Status.IN_PROGRESS, Booking.Status.COMPLETED]:
                booking.started_at = scheduled
            if status == Booking.Status.COMPLETED:
                booking.completed_at = scheduled + timedelta(hours=float(hours))
            booking.save()
            booking_count += 1

            if status == Booking.Status.COMPLETED:
                payment = Payment.objects.create(
                    booking=booking, amount=booking.price, method=random.choice(["upi", "card", "wallet", "cash"]),
                    status=Payment.Status.SUCCESS, paid_at=booking.completed_at,
                )
                if random.random() < 0.8:
                    Rating.objects.create(
                        booking=booking, customer=customer,
                        score=random.choice([4, 5, 5, 5, 3]),
                        comment=random.choice([
                            "Great work, very professional!", "On time and did a clean job.",
                            "Good service, would book again.", "Solved the issue quickly.",
                            "Satisfied with the work done.",
                        ]),
                    )
                    worker_profile.recalc_rating()

        self.stdout.write(self.style.SUCCESS(
            f"Done! Seeded {len(categories)} categories, {len(customers)} customers, "
            f"{len(workers)} workers, {booking_count} bookings."
        ))
        self.stdout.write(self.style.SUCCESS(
            "Login as: admin/coopadmin123 | rakesh_electrician/worker@123 | priya_customer/customer@123"
        ))
