from .base import *
import os


WEBSITE_BASE_URL = "http://localhost:3000" # react frontend
WEBSITE_BACKEND_URL = "http://localhost:8000"

DEBUG = False
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}
