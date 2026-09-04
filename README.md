# Cooperative Gig Services Platform (MVP)

A responsive web application that connects customers with verified local
cooperative workers (electricians, plumbers, carpenters, cleaners, painters,
gardeners, drivers, technicians).

Built with **Django 5**, **Bootstrap 5**, **Leaflet + OpenStreetMap**, and
**Chart.js**. Ships with realistic seed data and three role-based
dashboards: Customer, Worker, and Cooperative Admin.

## Features

- **Customer flow**: register/login → select service → find nearby verified
  workers (Leaflet map, distance-sorted) → view worker profile → book →
  track booking status → mock payment → invoice → rate worker.
- **Worker flow**: register/login → create skill profile → upload
  certificate → wait for admin verification → go online/offline →
  accept/reject bookings → update job status → view earnings (Chart.js).
- **Cooperative Admin flow**: dashboard with analytics (Chart.js) → verify
  workers → manage workers → manage service categories → manage bookings →
  monitor payments.
- **Emergency service**: customers can request the nearest *online*
  verified worker for a category with one tap.
- **Multilingual-ready UI**: English, Hindi (हिन्दी), and Gujarati
  (ગુજરાતી) via Django's i18n framework and a navbar language switcher.
- Fully responsive (mobile/tablet/desktop) using Bootstrap 5.

## Tech stack

| Layer          | Choice                                   |
|----------------|-------------------------------------------|
| Frontend       | HTML, CSS, JavaScript, Bootstrap 5         |
| Backend        | Python 3 + Django 5                        |
| Database       | SQLite (default local/dev)                 |
| Auth           | Django's built-in authentication           |
| Maps           | Leaflet + OpenStreetMap tiles              |
| Charts         | Chart.js                                   |
| Payments       | Mock gateway (no real transactions)        |
| Static files   | WhiteNoise                                 |
| Hosting        | Render (gunicorn + Procfile included)      |

## Quick start (local demo, SQLite)

```bash
python3 -m venv venv
source venv/bin/activate           # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_demo_data    # creates categories, workers, customers, bookings
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`.

### Demo logins (created by `seed_demo_data`)

| Role               | Username              | Password       |
|--------------------|------------------------|----------------|
| Cooperative Admin  | `admin`                | `coopadmin123` |
| Verified Worker    | `rakesh_electrician`   | `worker@123`   |
| Unverified Worker  | `vijay_electrician`    | `worker@123`   |
| Customer           | `priya_customer`       | `customer@123` |

(Other seeded workers: `suresh_plumber`, `manoj_carpenter`, `geeta_cleaner`,
`kiran_painter`, `dilip_gardener`, `hitesh_driver`, `nilesh_technician`,
`ramesh_plumber` — all use password `worker@123`. Other customers:
`amit_customer`, `sneha_customer`, `rahul_customer`, password
`customer@123`.)

Re-run `python manage.py seed_demo_data --flush` at any time to wipe and
regenerate demo data.

## Using a different database backend

SQLite is the default database for local development and demo use. If you want
an external database instead, set a `DATABASE_URL` connection string before
running migrations:

```bash
export DATABASE_URL=postgres://user:password@host:5432/coopgig
# or
export DATABASE_URL=mysql://user:password@host:3306/coopgig
```

This value takes priority over the default SQLite configuration. The project
also supports `DB_ENGINE=mysql` for explicit MySQL settings, but the built-in
local default remains SQLite.

## Deploying to Render

1. Push this project to a Git repository.
2. Create a new **Web Service** on Render, pointing at the repo.
3. Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
4. Start command is already provided via `Procfile`
   (`gunicorn coopgig.wsgi:application --bind 0.0.0.0:$PORT`), and the
   `release` line runs migrations automatically on each deploy.
5. Add a managed database in your hosting platform and set `DATABASE_URL`
   (or the `DB_*` variables) plus `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`,
   and `DJANGO_ALLOWED_HOSTS=<your-app>.onrender.com` in the Render
   environment settings.
6. After first deploy, run `python manage.py seed_demo_data` from the
   Render shell to populate demo data (optional).

## Project structure

```
coopgig/          Django project settings, urls, wsgi/asgi
accounts/         Custom User model (customer/worker/admin roles), auth views
services/         ServiceCategory + WorkerProfile models
bookings/         Booking + Rating models
payments/         Mock Payment model & commission logic
customers/        Customer-facing views (search, booking, payment, invoice…)
workers/          Worker-facing views (skill profile, bookings, earnings)
adminpanel/       Cooperative admin dashboard & management views
core/              Home page, shared utils (haversine distance), seed command
templates/         All HTML templates (Bootstrap 5)
static/            Custom CSS
locale/            Hindi & Gujarati translation files
```

## Notes on scope (MVP)

- Payments are fully mocked — no real payment gateway is integrated; every
  submitted payment is marked successful for demo purposes.
- Distance-based worker matching uses the haversine formula in
  `core/utils.py` and browser geolocation (with a graceful fallback to a
  default city center) — no external geocoding API is required.
- Translation coverage focuses on the highest-visibility UI strings
  (navigation, buttons, headings, statuses); a few less common form labels
  may still show in English. Extend `locale/*/LC_MESSAGES/django.po` and
  run `python manage.py compilemessages` to add more.
