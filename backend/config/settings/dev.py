"""Development settings."""
import os
from pathlib import Path

from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# Debug toolbar
INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405

# Query monitoring middleware (only in DEBUG)
MIDDLEWARE += [  # noqa: F405
    "apps.core.middleware.QueryCountMiddleware",
    "apps.core.middleware.SlowQueryMiddleware",
]

INTERNAL_IPS = ["127.0.0.1"]

# CORS - Allow both HTTP and HTTPS for local development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://localhost:3000",
    "https://127.0.0.1:3000",
]

# SSL Certificate paths for HTTPS development
CERTS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "certs"
SSL_CERTIFICATE = CERTS_DIR / "localhost.crt"
SSL_KEY = CERTS_DIR / "localhost.key"

# Show all SQL queries in console
LOGGING["loggers"]["django.db.backends"] = {  # noqa: F405
    "handlers": ["console"],
    "level": "DEBUG" if DEBUG else "INFO",
}

# Less strict throttling for development
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {  # noqa: F405
    "anon": "1000/hour",
    "user": "10000/hour",
}

