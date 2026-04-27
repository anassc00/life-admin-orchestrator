from .base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Use SQLite in development if PostgreSQL is not available
import os

if os.getenv("USE_SQLITE", "false").lower() == "true":
    DATABASES = {  # type: ignore[assignment]
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",  # type: ignore[name-defined]
        }
    }
