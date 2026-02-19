"""
Django settings for ARS_MP project.

Argentinian Rolling Stock Maintenance Planner.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env only outside Railway to avoid precedence conflicts.
if not os.getenv("RAILWAY_ENVIRONMENT"):
    load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# =============================================================================
# Security Settings
# =============================================================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-dev-only-change-in-production",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() in ("true", "1", "yes")

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Railway deployment: allow all .railway.app subdomains
if os.getenv("RAILWAY_ENVIRONMENT"):
    ALLOWED_HOSTS.append(".railway.app")

# CSRF trusted origins for Railway/production
CSRF_TRUSTED_ORIGINS = os.getenv(
    "CSRF_TRUSTED_ORIGINS",
    "http://localhost:8000,http://127.0.0.1:8000"
).split(",")

# Railway deployment: add CSRF trusted origin
if os.getenv("RAILWAY_ENVIRONMENT"):
    CSRF_TRUSTED_ORIGINS.append("https://web-production-77ceb.up.railway.app")

# Internal IPs for django-browser-reload
INTERNAL_IPS = ["127.0.0.1"]

# Security settings for production (Railway)
if os.getenv("RAILWAY_ENVIRONMENT"):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    # SESSION_COOKIE_SECURE = True  # Disabled for debugging
    # CSRF_COOKIE_SECURE = True  # Disabled for debugging


# =============================================================================
# Application definition
# =============================================================================

INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "tailwind",
    "theme",
    # Project apps
    "web.fleet",
    "infrastructure.database",
]

# Only enable browser reload in development
if DEBUG and not os.getenv("RAILWAY_ENVIRONMENT"):
    INSTALLED_APPS.append("django_browser_reload")

# Tailwind CSS configuration
TAILWIND_APP_NAME = "theme"

# NPM executable path (Windows)
NPM_BIN_PATH = "npm"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Only enable browser reload middleware in development
if DEBUG and not os.getenv("RAILWAY_ENVIRONMENT"):
    MIDDLEWARE.append("django_browser_reload.middleware.BrowserReloadMiddleware")

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# =============================================================================
# Database
# =============================================================================

DB_ENGINE = os.getenv("DJANGO_DB_ENGINE", "sqlite").lower()

IS_RAILWAY = bool(os.getenv("RAILWAY_ENVIRONMENT"))

# Support both POSTGRES_* (local docker) and PG* (Railway) variable names.
# Railway must prioritize PG* vars to avoid accidental .env precedence.
if DB_ENGINE == "postgres" or os.getenv("POSTGRES_DB") or os.getenv("PGDATABASE"):
    if IS_RAILWAY:
        db_name = os.getenv("PGDATABASE") or os.getenv("POSTGRES_DB", "ars_mp")
        db_user = os.getenv("PGUSER") or os.getenv("POSTGRES_USER", "ars_mp")
        db_password = os.getenv("PGPASSWORD") or os.getenv("POSTGRES_PASSWORD", "ars_mp")
        db_host = os.getenv("PGHOST") or os.getenv("POSTGRES_HOST", "localhost")
        db_port = os.getenv("PGPORT") or os.getenv("POSTGRES_PORT", "5432")
    else:
        db_name = os.getenv("POSTGRES_DB") or os.getenv("PGDATABASE", "ars_mp")
        db_user = os.getenv("POSTGRES_USER") or os.getenv("PGUSER", "ars_mp")
        db_password = os.getenv("POSTGRES_PASSWORD") or os.getenv("PGPASSWORD", "ars_mp")
        db_host = os.getenv("POSTGRES_HOST") or os.getenv("PGHOST", "localhost")
        db_port = os.getenv("POSTGRES_PORT") or os.getenv("PGPORT", "5432")

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": db_name,
            "USER": db_user,
            "PASSWORD": db_password,
            "HOST": db_host,
            "PORT": db_port,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# =============================================================================
# Authentication
# =============================================================================

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/fleet/modules/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

# Password hashers — Argon2 primary (OWASP recommended), PBKDF2 fallback
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
]


# =============================================================================
# Password validation
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# =============================================================================
# Internationalization
# =============================================================================

LANGUAGE_CODE = "es-ar"

TIME_ZONE = "America/Argentina/Buenos_Aires"

USE_I18N = True

USE_TZ = True


# =============================================================================
# Static files (CSS, JavaScript, Images)
# =============================================================================

STATIC_URL = "static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
    BASE_DIR / "theme" / "static",
    BASE_DIR / "web" / "static",
]

# Production static files (collectstatic output)
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise compression and caching
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# =============================================================================
# Default primary key field type
# =============================================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =============================================================================
# Logging
# =============================================================================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "etl": {
            "handlers": ["console"],
            "level": os.getenv("ETL_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "core": {
            "handlers": ["console"],
            "level": os.getenv("CORE_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "web": {
            "handlers": ["console"],
            "level": os.getenv("WEB_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}
