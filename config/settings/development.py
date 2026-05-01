from decouple import config

from .base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Use SQLite in development if PostgreSQL is not available.
# Set USE_SQLITE=true in .env to activate.
if config("USE_SQLITE", default="false", cast=bool):
    DATABASES = {  # type: ignore[assignment]
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",  # type: ignore[name-defined]
        }
    }
