import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "change-me-in-production-use-a-long-random-string",
)

DEBUG = os.environ.get("DEBUG", "False").lower() in ("true", "1", "yes")

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rest_framework",
    "bridge",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Karachi"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "bridge.authentication.BridgeAPIKeyAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "UNAUTHENTICATED_USER": None,
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
}

# Bridge API key — your ERP must send this in the X-API-Key header
BRIDGE_API_KEY = os.environ.get("BRIDGE_API_KEY", "")

# FBR configuration
FBR_ENVIRONMENT = os.environ.get("FBR_ENVIRONMENT", "sandbox").lower()

FBR_BASE_URLS = {
    "sandbox": os.environ.get(
        "FBR_SANDBOX_BASE_URL",
        "https://esp.fbr.gov.pk:8244",
    ),
    "sandbox_ssl": os.environ.get(
        "FBR_SANDBOX_SSL_BASE_URL",
        "https://gw.fbr.gov.pk",
    ),
    "production": os.environ.get(
        "FBR_PRODUCTION_BASE_URL",
        "https://gw.fbr.gov.pk/pdi/v1/api",
    ),
}

FBR_SECURITY_TOKEN = os.environ.get("FBR_SECURITY_TOKEN", "")

FBR_REQUEST_TIMEOUT = int(os.environ.get("FBR_REQUEST_TIMEOUT", "60"))

FBR_VERIFY_SSL = os.environ.get("FBR_VERIFY_SSL", "True").lower() in ("true", "1", "yes")

# Known FBR endpoint paths (relative to base URL)
FBR_ENDPOINTS = {
    "post_invoice": os.environ.get(
        "FBR_POST_INVOICE_ENDPOINT",
        "di_data/v1/di/postinvoicedata",
    ),
    "get_invoice_details": os.environ.get(
        "FBR_GET_INVOICE_DETAILS_ENDPOINT",
        "DigitalInvoicing/v1/GetInvoiceDetails",
    ),
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{asctime} {levelname} {name} {message}",
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
        "bridge": {
            "handlers": ["console"],
            "level": os.environ.get("LOG_LEVEL", "INFO"),
        },
    },
}
