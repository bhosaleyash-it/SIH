"""
Django settings for Cooperative Gig Services Platform.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "dev-insecure-secret-key-change-in-production-coopgig-2026",
)

DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "accounts",
    "services",
    "bookings",
    "payments",
    "core",
    "customers",
    "workers",
    "adminpanel",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "coopgig.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "core.context_processors.site_context",
            ],
        },
    },
]

WSGI_APPLICATION = "coopgig.wsgi.application"

# ---------------------------------------------------------------------------
# Database
# By default uses SQLite for zero-config local development / demo.
# On Render (or similar), set DATABASE_URL to auto-configure via dj-database-url
# (works with managed Postgres or MySQL connection strings).
# Alternatively set DB_ENGINE=mysql plus DB_NAME/DB_USER/DB_PASSWORD/DB_HOST/DB_PORT.
# ---------------------------------------------------------------------------
import dj_database_url

if os.environ.get("DATABASE_URL"):
    DATABASES = {
        "default": dj_database_url.config(
            env="DATABASE_URL", conn_max_age=600, ssl_require=os.environ.get("DB_SSL_REQUIRE", "False") == "True"
        )
    }
elif os.environ.get("DB_ENGINE") == "mysql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.environ.get("DB_NAME", "coopgig"),
            "USER": os.environ.get("DB_USER", "coopgig"),
            "PASSWORD": os.environ.get("DB_PASSWORD", ""),
            "HOST": os.environ.get("DB_HOST", "localhost"),
            "PORT": os.environ.get("DB_PORT", "3306"),
            "OPTIONS": {"charset": "utf8mb4"},
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 6}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Internationalization - English, Hindi, Gujarati
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ("en", "English"),
    ("hi", "हिन्दी (Hindi)"),
    ("gu", "ગુજરાતી (Gujarati)"),
]

LOCALE_PATHS = [BASE_DIR / "locale"]

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
WHITENOISE_USE_FINDERS = DEBUG

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "core:post_login_redirect"
LOGOUT_REDIRECT_URL = "core:home"

MESSAGE_TAGS = {
    10: "info", 20: "info", 25: "success", 30: "warning", 40: "danger",
}

# Mock payment settings
MOCK_PAYMENT_SUCCESS_RATE = 1.0  # MVP: always succeed for demo reliability
PLATFORM_COMMISSION_PERCENT = 15  # cooperative commission on each booking
