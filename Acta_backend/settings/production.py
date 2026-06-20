"""
Production settings for Acta_backend project.
"""

from .base import *
from decouple import config
import os
import dj_database_url

SECRET_KEY = config('DJANGO_SECRET_KEY', default=config('SECRET_KEY', default='django-insecure-prod-fallback-key'))


# Debug
DEBUG = config('DEBUG', default=False, cast=bool)

# Allowed hosts
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,acta-backend-vcbr.onrender.com,acta-backend-ajqf.onrender.com', cast=lambda v: [s.strip() for s in v.split(',')])

render_hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if render_hostname:
    ALLOWED_HOSTS.append(render_hostname)


# Database
ssl_require = config('DATABASE_SSL_REQUIRE', default=True, cast=bool)
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default=config('DB_URL', default='')),
        conn_max_age=600,
        ssl_require=ssl_require
    )
}

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 31536000
SECURE_REDIRECT_EXEMPT = []
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Session Security
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# CORS Settings for production
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='https://acta-psi.vercel.app,http://localhost:3000',
    cast=lambda v: [s.strip() for s in v.split(',')]
)
CORS_ALLOW_CREDENTIALS = True

# Logging for production
# Logging for production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}


# Configure S3-compatible storage (Cloudflare R2)
USE_S3 = config("USE_S3", default="False") == "True"

if USE_S3:
    if 'storages' not in INSTALLED_APPS:
        INSTALLED_APPS.append('storages')
    
    AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME", default="auto")
    AWS_S3_ENDPOINT_URL = config("AWS_S3_ENDPOINT_URL")
    AWS_S3_CUSTOM_DOMAIN = config("AWS_S3_CUSTOM_DOMAIN", default=None)
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None
    AWS_QUERYSTRING_AUTH = config("AWS_QUERYSTRING_AUTH", default="False") == "True"

    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.StaticFilesStorage",
        },
    }

    if AWS_S3_CUSTOM_DOMAIN:
        MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"
    else:
        # Construct endpoint url with bucket name
        MEDIA_URL = f"{AWS_S3_ENDPOINT_URL.rstrip('/')}/{AWS_STORAGE_BUCKET_NAME}/"
else:
    # Use default local settings if S3 is disabled in production
    MEDIA_URL = '/media/'