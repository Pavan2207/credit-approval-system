"""
Test settings for local development without Docker.
Uses SQLite for simpler local testing.
"""
from .settings import *

# Override database to use SQLite for local testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Use synchronous task execution for local testing
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

