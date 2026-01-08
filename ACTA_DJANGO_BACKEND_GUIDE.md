# Acta Django Backend - Comprehensive Development Guide

> A complete guide to building the Acta backend with Django REST Framework

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Tech Stack](#2-tech-stack)
3. [Project Setup](#3-project-setup)
4. [Project Structure](#4-project-structure)
5. [Configuration](#5-configuration)
6. [Database Models](#6-database-models)
7. [Serializers](#7-serializers)
8. [Views & ViewSets](#8-views--viewsets)
9. [API Endpoints](#9-api-endpoints)
10. [URL Configuration](#10-url-configuration)
11. [Authentication](#11-authentication)
12. [Permissions](#12-permissions)
13. [Filters & Search](#13-filters--search)
14. [Signals](#14-signals)
15. [Management Commands](#15-management-commands)
16. [Testing](#16-testing)
17. [Deployment](#17-deployment)
18. [Frontend Integration](#18-frontend-integration)

---

## 1. Project Overview

Acta is a modern task management application with the following features:

- **User Authentication**: Registration, login, logout, password reset
- **Task Management**: Create, read, update, delete tasks
- **Task Organization**: Priority levels, status tracking, due dates, categories
- **Completed Tasks**: Track tasks completed in the last 7 days
- **Analytics**: Task completion statistics and productivity metrics
- **User Profiles**: Customizable user profiles with avatars
- **Settings**: User preferences and application settings

---

## 2. Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | Django 5.x |
| API | Django REST Framework 3.15+ |
| Database | PostgreSQL 15+ |
| Authentication | JWT (djangorestframework-simplejwt) |
| CORS | django-cors-headers |
| Filtering | django-filter |
| File Storage | Django Storages + AWS S3 (or local) |
| Task Queue | Celery + Redis (optional) |
| Documentation | drf-spectacular (OpenAPI) |

---

## 3. Project Setup

### 3.1 Create Virtual Environment

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### 3.2 Install Dependencies

```bash
# Create requirements.txt
pip install django djangorestframework djangorestframework-simplejwt
pip install django-cors-headers django-filter drf-spectacular
pip install psycopg2-binary python-decouple pillow
pip install celery redis  # Optional: for background tasks

# Save dependencies
pip freeze > requirements.txt
```

### 3.3 Create Django Project

```bash
# Create project
django-admin startproject Acta_backend .

# Create apps
python manage.py startapp accounts
python manage.py startapp tasks
python manage.py startapp analytics
```

---

## 4. Project Structure

```
Acta_backend/
├── manage.py
├── requirements.txt
├── .env
├── .env.example
├── Acta_backend/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── permissions.py
│   ├── signals.py
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py
│       ├── test_views.py
│       └── test_serializers.py
├── tasks/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── filters.py
│   ├── signals.py
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py
│       ├── test_views.py
│       └── test_serializers.py
├── analytics/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── services.py
├── core/
│   ├── __init__.py
│   ├── pagination.py
│   ├── permissions.py
│   ├── exceptions.py
│   └── utils.py
└── media/
    └── avatars/
```

---

## 5. Configuration

### 5.1 Environment Variables (.env)

```env
# .env
DEBUG=True
SECRET_KEY=your-super-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgres://user:password@localhost:5432/Acta_db
# Or individual settings:
DB_NAME=Acta_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=60  # minutes
JWT_REFRESH_TOKEN_LIFETIME=7  # days

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# AWS S3 (optional - for file storage)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=Acta-bucket
AWS_S3_REGION_NAME=us-east-1
```

### 5.2 Base Settings (Acta_backend/settings/base.py)

```python
"""
Base settings for Acta project.
"""
import os
from pathlib import Path
from datetime import timedelta
from decouple import config, Csv

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Security
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='', cast=Csv())

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
]

LOCAL_APPS = [
    'accounts.apps.AccountsConfig',
    'tasks.apps.TasksConfig',
    'analytics.apps.AnalyticsConfig',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Must be first
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Acta_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Acta_backend.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='Acta_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# Django REST Framework Configuration
# =============================================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'core.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
    'EXCEPTION_HANDLER': 'core.exceptions.custom_exception_handler',
}

# =============================================================================
# JWT Configuration
# =============================================================================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=config('JWT_ACCESS_TOKEN_LIFETIME', default=60, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=config('JWT_REFRESH_TOKEN_LIFETIME', default=7, cast=int)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# =============================================================================
# CORS Configuration
# =============================================================================
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:5173',
    cast=Csv()
)
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# =============================================================================
# API Documentation (drf-spectacular)
# =============================================================================
SPECTACULAR_SETTINGS = {
    'TITLE': 'Acta API',
    'DESCRIPTION': 'A comprehensive task management API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/v1',
}
```

### 5.3 Development Settings (Acta_backend/settings/development.py)

```python
"""
Development settings for Acta project.
"""
from .base import *

DEBUG = True

# Use SQLite for development (optional)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable throttling in development
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []
```

### 5.4 Production Settings (Acta_backend/settings/production.py)

```python
"""
Production settings for Acta project.
"""
from .base import *

DEBUG = False

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

# HSTS settings
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# AWS S3 Storage (optional)
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
# AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
# AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
# AWS_S3_FILE_OVERWRITE = False
# AWS_DEFAULT_ACL = None
```

---

## 6. Database Models

### 6.1 Accounts App Models (accounts/models.py)

```python
"""
User and Profile models for Acta.
"""
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom user manager for Acta."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user."""
        if not email:
            raise ValueError('Users must have an email address')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model using email as the unique identifier."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip() or self.email
    
    def get_initials(self):
        """Return user's initials for avatar fallback."""
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        return self.email[0].upper()


class Profile(models.Model):
    """Extended user profile information."""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        primary_key=True
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True
    )
    bio = models.TextField(max_length=500, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    task_reminders = models.BooleanField(default=True)
    
    # UI preferences
    theme = models.CharField(
        max_length=20,
        choices=[
            ('light', 'Light'),
            ('dark', 'Dark'),
            ('system', 'System'),
        ],
        default='system'
    )
    sidebar_collapsed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'profiles'
        verbose_name = 'profile'
        verbose_name_plural = 'profiles'
    
    def __str__(self):
        return f"Profile for {self.user.email}"


class UserRole(models.Model):
    """
    User roles for authorization.
    IMPORTANT: Roles stored separately to prevent privilege escalation.
    """
    
    class RoleType(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        MODERATOR = 'moderator', 'Moderator'
        USER = 'user', 'User'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='roles'
    )
    role = models.CharField(
        max_length=20,
        choices=RoleType.choices,
        default=RoleType.USER
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_roles'
        unique_together = ['user', 'role']
        verbose_name = 'user role'
        verbose_name_plural = 'user roles'
    
    def __str__(self):
        return f"{self.user.email} - {self.role}"
```

### 6.2 Tasks App Models (tasks/models.py)

```python
"""
Task models for Acta.
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class Category(models.Model):
    """Task categories for organization."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#6366f1')  # Hex color
    icon = models.CharField(max_length=50, blank=True)  # Icon name
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='categories'
    )
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'category'
        verbose_name_plural = 'categories'
        unique_together = ['name', 'user']
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Task(models.Model):
    """Main task model."""
    
    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    # Dates and times
    due_date = models.DateField(null=True, blank=True)
    due_time = models.TimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Relationships
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks'
    )
    
    # Optional: Assignee (for team features)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    
    # Metadata
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.JSONField(null=True, blank=True)
    # Example: {"type": "daily", "interval": 1} or {"type": "weekly", "days": [1, 3, 5]}
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tasks'
        verbose_name = 'task'
        verbose_name_plural = 'tasks'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'due_date']),
            models.Index(fields=['user', 'priority']),
            models.Index(fields=['status', 'completed_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Handle status change to completed."""
        if self.status == self.Status.COMPLETED and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != self.Status.COMPLETED:
            self.completed_at = None
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        """Check if task is overdue."""
        if self.due_date and self.status != self.Status.COMPLETED:
            today = timezone.now().date()
            return self.due_date < today
        return False
    
    @property
    def is_due_today(self):
        """Check if task is due today."""
        if self.due_date:
            today = timezone.now().date()
            return self.due_date == today
        return False


class TaskComment(models.Model):
    """Comments on tasks."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='task_comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'task_comments'
        verbose_name = 'task comment'
        verbose_name_plural = 'task comments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.user.email} on {self.task.title}"


class TaskAttachment(models.Model):
    """File attachments for tasks."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file = models.FileField(upload_to='task_attachments/')
    filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()  # In bytes
    file_type = models.CharField(max_length=100)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_attachments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'task_attachments'
        verbose_name = 'task attachment'
        verbose_name_plural = 'task attachments'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.filename
```

### 6.3 Analytics Models (analytics/models.py)

```python
"""
Analytics models for Acta.
"""
import uuid
from django.db import models
from django.conf import settings


class DailyStats(models.Model):
    """Daily aggregated statistics per user."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='daily_stats'
    )
    date = models.DateField()
    
    tasks_created = models.PositiveIntegerField(default=0)
    tasks_completed = models.PositiveIntegerField(default=0)
    tasks_overdue = models.PositiveIntegerField(default=0)
    
    # Time tracking (optional)
    total_focus_time = models.PositiveIntegerField(default=0)  # In minutes
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'daily_stats'
        verbose_name = 'daily stats'
        verbose_name_plural = 'daily stats'
        unique_together = ['user', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"Stats for {self.user.email} on {self.date}"


class WeeklyStats(models.Model):
    """Weekly aggregated statistics per user."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='weekly_stats'
    )
    week_start = models.DateField()  # Monday of the week
    week_end = models.DateField()    # Sunday of the week
    
    tasks_created = models.PositiveIntegerField(default=0)
    tasks_completed = models.PositiveIntegerField(default=0)
    completion_rate = models.FloatField(default=0.0)  # Percentage
    
    most_productive_day = models.CharField(max_length=10, blank=True)
    average_tasks_per_day = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'weekly_stats'
        verbose_name = 'weekly stats'
        verbose_name_plural = 'weekly stats'
        unique_together = ['user', 'week_start']
        ordering = ['-week_start']
    
    def __str__(self):
        return f"Week stats for {self.user.email} ({self.week_start})"
```

---

## 7. Serializers

### 7.1 Account Serializers (accounts/serializers.py)

```python
"""
Serializers for user authentication and profiles.
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Profile, UserRole

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'password', 'password_confirm'
        ]
        read_only_fields = ['id']
    
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': "Passwords don't match."
            })
        return attrs
    
    def create(self, validated_data):
        """Create user with hashed password."""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer with additional user data."""
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add custom claims
        data['user'] = {
            'id': str(self.user.id),
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'full_name': self.user.full_name,
        }
        
        return data
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims to the token
        token['email'] = user.email
        token['full_name'] = user.full_name
        
        return token


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""
    
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    initials = serializers.CharField(source='user.get_initials', read_only=True)
    
    class Meta:
        model = Profile
        fields = [
            'email', 'first_name', 'last_name', 'full_name', 'initials',
            'avatar', 'bio', 'phone', 'timezone',
            'email_notifications', 'push_notifications', 'task_reminders',
            'theme', 'sidebar_collapsed',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def update(self, instance, validated_data):
        """Update profile and nested user fields."""
        user_data = validated_data.pop('user', {})
        
        # Update user fields
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()
        
        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer for references."""
    
    full_name = serializers.CharField(read_only=True)
    initials = serializers.CharField(source='get_initials', read_only=True)
    avatar = serializers.ImageField(source='profile.avatar', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'initials', 'avatar']
        read_only_fields = fields


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change."""
    
    old_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': "Passwords don't match."
            })
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request."""
    
    email = serializers.EmailField()
    
    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            # Don't reveal if email exists
            pass
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation."""
    
    token = serializers.CharField()
    new_password = serializers.CharField(
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': "Passwords don't match."
            })
        return attrs
```

### 7.2 Task Serializers (tasks/serializers.py)

```python
"""
Serializers for tasks.
"""
from rest_framework import serializers
from .models import Task, Category, TaskComment, TaskAttachment
from accounts.serializers import UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for task categories."""
    
    task_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'color', 'icon', 'is_default', 'task_count', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_task_count(self, obj):
        return obj.tasks.count()
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TaskCommentSerializer(serializers.ModelSerializer):
    """Serializer for task comments."""
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = TaskComment
        fields = ['id', 'user', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['task_id'] = self.context['task_id']
        return super().create(validated_data)


class TaskAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for task attachments."""
    
    uploaded_by = UserSerializer(read_only=True)
    
    class Meta:
        model = TaskAttachment
        fields = ['id', 'file', 'filename', 'file_size', 'file_type', 'uploaded_by', 'created_at']
        read_only_fields = ['id', 'filename', 'file_size', 'file_type', 'uploaded_by', 'created_at']
    
    def create(self, validated_data):
        file = validated_data['file']
        validated_data['filename'] = file.name
        validated_data['file_size'] = file.size
        validated_data['file_type'] = file.content_type
        validated_data['uploaded_by'] = self.context['request'].user
        validated_data['task_id'] = self.context['task_id']
        return super().create(validated_data)


class TaskListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for task lists."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    is_due_today = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'priority', 'status',
            'due_date', 'due_time', 'category', 'category_name',
            'is_overdue', 'is_due_today', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class TaskDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single task view."""
    
    user = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    assigned_to_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    comments = TaskCommentSerializer(many=True, read_only=True)
    attachments = TaskAttachmentSerializer(many=True, read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    is_due_today = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'priority', 'status',
            'due_date', 'due_time', 'completed_at',
            'user', 'category', 'category_id',
            'assigned_to', 'assigned_to_id',
            'is_recurring', 'recurrence_pattern',
            'is_overdue', 'is_due_today',
            'comments', 'attachments',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'completed_at', 'created_at', 'updated_at']


class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tasks."""
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'priority', 'status',
            'due_date', 'due_time', 'category', 'assigned_to',
            'is_recurring', 'recurrence_pattern'
        ]
        read_only_fields = ['id']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TaskUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating tasks."""
    
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'priority', 'status',
            'due_date', 'due_time', 'category', 'assigned_to',
            'is_recurring', 'recurrence_pattern'
        ]


class TaskStatusUpdateSerializer(serializers.Serializer):
    """Serializer for quick status updates."""
    
    status = serializers.ChoiceField(choices=Task.Status.choices)


class BulkTaskActionSerializer(serializers.Serializer):
    """Serializer for bulk task operations."""
    
    task_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1
    )
    action = serializers.ChoiceField(choices=[
        ('complete', 'Mark as Completed'),
        ('delete', 'Delete'),
        ('change_priority', 'Change Priority'),
        ('change_status', 'Change Status'),
    ])
    value = serializers.CharField(required=False, allow_blank=True)
```

### 7.3 Analytics Serializers (analytics/serializers.py)

```python
"""
Serializers for analytics.
"""
from rest_framework import serializers
from .models import DailyStats, WeeklyStats


class DailyStatsSerializer(serializers.ModelSerializer):
    """Serializer for daily statistics."""
    
    completion_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = DailyStats
        fields = [
            'id', 'date', 'tasks_created', 'tasks_completed',
            'tasks_overdue', 'total_focus_time', 'completion_rate'
        ]
    
    def get_completion_rate(self, obj):
        if obj.tasks_created == 0:
            return 0.0
        return round((obj.tasks_completed / obj.tasks_created) * 100, 1)


class WeeklyStatsSerializer(serializers.ModelSerializer):
    """Serializer for weekly statistics."""
    
    class Meta:
        model = WeeklyStats
        fields = [
            'id', 'week_start', 'week_end',
            'tasks_created', 'tasks_completed', 'completion_rate',
            'most_productive_day', 'average_tasks_per_day'
        ]


class OverviewStatsSerializer(serializers.Serializer):
    """Serializer for overview dashboard statistics."""
    
    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    pending_tasks = serializers.IntegerField()
    in_progress_tasks = serializers.IntegerField()
    overdue_tasks = serializers.IntegerField()
    due_today = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    tasks_this_week = serializers.IntegerField()
    completed_this_week = serializers.IntegerField()


class ProductivityTrendSerializer(serializers.Serializer):
    """Serializer for productivity trends."""
    
    date = serializers.DateField()
    tasks_created = serializers.IntegerField()
    tasks_completed = serializers.IntegerField()


class CategoryStatsSerializer(serializers.Serializer):
    """Serializer for category-wise statistics."""
    
    category_id = serializers.UUIDField()
    category_name = serializers.CharField()
    category_color = serializers.CharField()
    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    completion_rate = serializers.FloatField()
```

---

## 8. Views & ViewSets

### 8.1 Account Views (accounts/views.py)

```python
"""
Views for user authentication and profiles.
"""
from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from .models import Profile
from .serializers import (
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    ProfileSerializer,
    UserSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """User registration endpoint."""
    
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom login endpoint with additional user data."""
    
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    """Logout endpoint - blacklist refresh token."""
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    """Get and update current user's profile."""
    
    serializer_class = ProfileSerializer
    parser_classes = [MultiPartParser, FormParser]
    
    def get_object(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile


class ChangePasswordView(generics.UpdateAPIView):
    """Change user password."""
    
    serializer_class = ChangePasswordSerializer
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = self.get_object()
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({'message': 'Password changed successfully'})


class PasswordResetRequestView(generics.CreateAPIView):
    """Request password reset email."""
    
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetRequestSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # TODO: Send password reset email
        # email = serializer.validated_data['email']
        # send_password_reset_email(email)
        
        return Response({
            'message': 'If an account exists with this email, a reset link will be sent.'
        })


class PasswordResetConfirmView(generics.CreateAPIView):
    """Confirm password reset with token."""
    
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetConfirmSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # TODO: Validate token and reset password
        
        return Response({'message': 'Password reset successful'})


class CurrentUserView(generics.RetrieveAPIView):
    """Get current authenticated user."""
    
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user
```

### 8.2 Task Views (tasks/views.py)

```python
"""
Views for tasks.
"""
from rest_framework import viewsets, status, generics, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta

from .models import Task, Category, TaskComment, TaskAttachment
from .serializers import (
    TaskListSerializer,
    TaskDetailSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer,
    TaskStatusUpdateSerializer,
    BulkTaskActionSerializer,
    CategorySerializer,
    TaskCommentSerializer,
    TaskAttachmentSerializer,
)
from .filters import TaskFilter


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tasks.
    
    list: Get all tasks for the current user
    create: Create a new task
    retrieve: Get a specific task
    update: Update a task
    partial_update: Partially update a task
    destroy: Delete a task
    """
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TaskFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'priority', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return tasks for the current user."""
        return Task.objects.filter(user=self.request.user).select_related('category', 'assigned_to')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return TaskListSerializer
        elif self.action == 'create':
            return TaskCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TaskUpdateSerializer
        return TaskDetailSerializer
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get tasks due today."""
        today = timezone.now().date()
        tasks = self.get_queryset().filter(due_date=today)
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue tasks."""
        today = timezone.now().date()
        tasks = self.get_queryset().filter(
            due_date__lt=today,
            status__in=[Task.Status.PENDING, Task.Status.IN_PROGRESS]
        )
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def completed(self, request):
        """Get tasks completed in the last 7 days."""
        seven_days_ago = timezone.now() - timedelta(days=7)
        tasks = self.get_queryset().filter(
            status=Task.Status.COMPLETED,
            completed_at__gte=seven_days_ago
        ).order_by('-completed_at')
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming tasks (next 7 days)."""
        today = timezone.now().date()
        next_week = today + timedelta(days=7)
        tasks = self.get_queryset().filter(
            due_date__gte=today,
            due_date__lte=next_week,
            status__in=[Task.Status.PENDING, Task.Status.IN_PROGRESS]
        ).order_by('due_date')
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Quick status update for a task."""
        task = self.get_object()
        serializer = TaskStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        task.status = serializer.validated_data['status']
        task.save()
        
        return Response(TaskDetailSerializer(task).data)
    
    @action(detail=True, methods=['post'])
    def toggle_complete(self, request, pk=None):
        """Toggle task completion status."""
        task = self.get_object()
        
        if task.status == Task.Status.COMPLETED:
            task.status = Task.Status.PENDING
            task.completed_at = None
        else:
            task.status = Task.Status.COMPLETED
            task.completed_at = timezone.now()
        
        task.save()
        return Response(TaskDetailSerializer(task).data)
    
    @action(detail=False, methods=['post'])
    def bulk_action(self, request):
        """Perform bulk actions on multiple tasks."""
        serializer = BulkTaskActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        task_ids = serializer.validated_data['task_ids']
        action = serializer.validated_data['action']
        value = serializer.validated_data.get('value')
        
        tasks = self.get_queryset().filter(id__in=task_ids)
        
        if action == 'complete':
            tasks.update(status=Task.Status.COMPLETED, completed_at=timezone.now())
        elif action == 'delete':
            tasks.delete()
            return Response({'message': f'{len(task_ids)} tasks deleted'})
        elif action == 'change_priority' and value:
            tasks.update(priority=value)
        elif action == 'change_status' and value:
            tasks.update(status=value)
        
        return Response({'message': f'Bulk action "{action}" applied to {len(task_ids)} tasks'})


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing task categories."""
    
    serializer_class = CategorySerializer
    
    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


class TaskCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing task comments."""
    
    serializer_class = TaskCommentSerializer
    
    def get_queryset(self):
        task_id = self.kwargs.get('task_pk')
        return TaskComment.objects.filter(
            task_id=task_id,
            task__user=self.request.user
        )
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['task_id'] = self.kwargs.get('task_pk')
        return context


class TaskAttachmentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing task attachments."""
    
    serializer_class = TaskAttachmentSerializer
    parser_classes = [MultiPartParser, FormParser]
    http_method_names = ['get', 'post', 'delete']  # No updates for attachments
    
    def get_queryset(self):
        task_id = self.kwargs.get('task_pk')
        return TaskAttachment.objects.filter(
            task_id=task_id,
            task__user=self.request.user
        )
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['task_id'] = self.kwargs.get('task_pk')
        return context
```

### 8.3 Analytics Views (analytics/views.py)

```python
"""
Views for analytics.
"""
from rest_framework import generics, views
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta

from tasks.models import Task, Category
from .models import DailyStats, WeeklyStats
from .serializers import (
    DailyStatsSerializer,
    WeeklyStatsSerializer,
    OverviewStatsSerializer,
    ProductivityTrendSerializer,
    CategoryStatsSerializer,
)


class OverviewStatsView(views.APIView):
    """Get overview statistics for the dashboard."""
    
    def get(self, request):
        user = request.user
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        
        tasks = Task.objects.filter(user=user)
        
        stats = {
            'total_tasks': tasks.count(),
            'completed_tasks': tasks.filter(status=Task.Status.COMPLETED).count(),
            'pending_tasks': tasks.filter(status=Task.Status.PENDING).count(),
            'in_progress_tasks': tasks.filter(status=Task.Status.IN_PROGRESS).count(),
            'overdue_tasks': tasks.filter(
                due_date__lt=today,
                status__in=[Task.Status.PENDING, Task.Status.IN_PROGRESS]
            ).count(),
            'due_today': tasks.filter(due_date=today).count(),
            'tasks_this_week': tasks.filter(created_at__date__gte=week_start).count(),
            'completed_this_week': tasks.filter(
                status=Task.Status.COMPLETED,
                completed_at__date__gte=week_start
            ).count(),
        }
        
        # Calculate completion rate
        if stats['total_tasks'] > 0:
            stats['completion_rate'] = round(
                (stats['completed_tasks'] / stats['total_tasks']) * 100, 1
            )
        else:
            stats['completion_rate'] = 0.0
        
        serializer = OverviewStatsSerializer(stats)
        return Response(serializer.data)


class DailyStatsView(generics.ListAPIView):
    """Get daily statistics for the last N days."""
    
    serializer_class = DailyStatsSerializer
    
    def get_queryset(self):
        days = int(self.request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        
        return DailyStats.objects.filter(
            user=self.request.user,
            date__gte=start_date
        ).order_by('date')


class WeeklyStatsView(generics.ListAPIView):
    """Get weekly statistics for the last N weeks."""
    
    serializer_class = WeeklyStatsSerializer
    
    def get_queryset(self):
        weeks = int(self.request.query_params.get('weeks', 12))
        today = timezone.now().date()
        start_date = today - timedelta(weeks=weeks)
        
        return WeeklyStats.objects.filter(
            user=self.request.user,
            week_start__gte=start_date
        ).order_by('week_start')


class ProductivityTrendView(views.APIView):
    """Get productivity trends for charting."""
    
    def get(self, request):
        days = int(request.query_params.get('days', 14))
        today = timezone.now().date()
        
        trends = []
        for i in range(days - 1, -1, -1):
            date = today - timedelta(days=i)
            tasks = Task.objects.filter(user=request.user)
            
            trends.append({
                'date': date,
                'tasks_created': tasks.filter(created_at__date=date).count(),
                'tasks_completed': tasks.filter(
                    status=Task.Status.COMPLETED,
                    completed_at__date=date
                ).count(),
            })
        
        serializer = ProductivityTrendSerializer(trends, many=True)
        return Response(serializer.data)


class CategoryStatsView(views.APIView):
    """Get statistics grouped by category."""
    
    def get(self, request):
        categories = Category.objects.filter(user=request.user).annotate(
            total_tasks=Count('tasks'),
            completed_tasks=Count('tasks', filter=Q(tasks__status=Task.Status.COMPLETED))
        )
        
        stats = []
        for category in categories:
            completion_rate = 0.0
            if category.total_tasks > 0:
                completion_rate = round(
                    (category.completed_tasks / category.total_tasks) * 100, 1
                )
            
            stats.append({
                'category_id': category.id,
                'category_name': category.name,
                'category_color': category.color,
                'total_tasks': category.total_tasks,
                'completed_tasks': category.completed_tasks,
                'completion_rate': completion_rate,
            })
        
        serializer = CategoryStatsSerializer(stats, many=True)
        return Response(serializer.data)
```

---

## 9. API Endpoints

### Complete API Reference

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| **Authentication** ||||
| POST | `/api/v1/auth/register/` | Register new user | ❌ |
| POST | `/api/v1/auth/login/` | Login (get tokens) | ❌ |
| POST | `/api/v1/auth/logout/` | Logout (blacklist token) | ✅ |
| POST | `/api/v1/auth/token/refresh/` | Refresh access token | ❌ |
| POST | `/api/v1/auth/password/reset/` | Request password reset | ❌ |
| POST | `/api/v1/auth/password/reset/confirm/` | Confirm password reset | ❌ |
| POST | `/api/v1/auth/password/change/` | Change password | ✅ |
| **User & Profile** ||||
| GET | `/api/v1/users/me/` | Get current user | ✅ |
| GET | `/api/v1/users/profile/` | Get user profile | ✅ |
| PUT/PATCH | `/api/v1/users/profile/` | Update user profile | ✅ |
| **Tasks** ||||
| GET | `/api/v1/tasks/` | List all tasks | ✅ |
| POST | `/api/v1/tasks/` | Create new task | ✅ |
| GET | `/api/v1/tasks/{id}/` | Get task details | ✅ |
| PUT | `/api/v1/tasks/{id}/` | Update task | ✅ |
| PATCH | `/api/v1/tasks/{id}/` | Partial update task | ✅ |
| DELETE | `/api/v1/tasks/{id}/` | Delete task | ✅ |
| GET | `/api/v1/tasks/today/` | Get tasks due today | ✅ |
| GET | `/api/v1/tasks/overdue/` | Get overdue tasks | ✅ |
| GET | `/api/v1/tasks/completed/` | Get completed tasks (7 days) | ✅ |
| GET | `/api/v1/tasks/upcoming/` | Get upcoming tasks (7 days) | ✅ |
| PATCH | `/api/v1/tasks/{id}/update_status/` | Quick status update | ✅ |
| POST | `/api/v1/tasks/{id}/toggle_complete/` | Toggle completion | ✅ |
| POST | `/api/v1/tasks/bulk_action/` | Bulk operations | ✅ |
| **Task Comments** ||||
| GET | `/api/v1/tasks/{task_id}/comments/` | List task comments | ✅ |
| POST | `/api/v1/tasks/{task_id}/comments/` | Add comment | ✅ |
| DELETE | `/api/v1/tasks/{task_id}/comments/{id}/` | Delete comment | ✅ |
| **Task Attachments** ||||
| GET | `/api/v1/tasks/{task_id}/attachments/` | List attachments | ✅ |
| POST | `/api/v1/tasks/{task_id}/attachments/` | Upload attachment | ✅ |
| DELETE | `/api/v1/tasks/{task_id}/attachments/{id}/` | Delete attachment | ✅ |
| **Categories** ||||
| GET | `/api/v1/categories/` | List categories | ✅ |
| POST | `/api/v1/categories/` | Create category | ✅ |
| PUT/PATCH | `/api/v1/categories/{id}/` | Update category | ✅ |
| DELETE | `/api/v1/categories/{id}/` | Delete category | ✅ |
| **Analytics** ||||
| GET | `/api/v1/analytics/overview/` | Overview statistics | ✅ |
| GET | `/api/v1/analytics/daily/` | Daily stats | ✅ |
| GET | `/api/v1/analytics/weekly/` | Weekly stats | ✅ |
| GET | `/api/v1/analytics/trends/` | Productivity trends | ✅ |
| GET | `/api/v1/analytics/categories/` | Category statistics | ✅ |

### Query Parameters

#### Tasks List Filtering
```
GET /api/v1/tasks/?status=pending&priority=high&category={uuid}&due_date=2026-01-05
GET /api/v1/tasks/?search=project&ordering=-due_date
GET /api/v1/tasks/?due_date__gte=2026-01-01&due_date__lte=2026-01-31
```

#### Pagination
```
GET /api/v1/tasks/?page=1&page_size=20
```

---

## 10. URL Configuration

### 10.1 Main URLs (Acta_backend/urls.py)

```python
"""
Main URL configuration for Acta.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API v1
    path('api/v1/', include([
        path('auth/', include('accounts.urls.auth_urls')),
        path('users/', include('accounts.urls.user_urls')),
        path('', include('tasks.urls')),
        path('analytics/', include('analytics.urls')),
    ])),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

### 10.2 Account URLs (accounts/urls/)

```python
# accounts/urls/__init__.py
# Empty file

# accounts/urls/auth_urls.py
"""Authentication URLs."""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views import (
    RegisterView,
    CustomTokenObtainPairView,
    LogoutView,
    ChangePasswordView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password/change/', ChangePasswordView.as_view(), name='password_change'),
    path('password/reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]

# accounts/urls/user_urls.py
"""User URLs."""
from django.urls import path
from accounts.views import CurrentUserView, ProfileView

urlpatterns = [
    path('me/', CurrentUserView.as_view(), name='current_user'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
```

### 10.3 Task URLs (tasks/urls.py)

```python
"""Task URLs with nested routes."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import TaskViewSet, CategoryViewSet, TaskCommentViewSet, TaskAttachmentViewSet

# Main router
router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'categories', CategoryViewSet, basename='category')

# Nested router for comments and attachments
tasks_router = routers.NestedDefaultRouter(router, r'tasks', lookup='task')
tasks_router.register(r'comments', TaskCommentViewSet, basename='task-comments')
tasks_router.register(r'attachments', TaskAttachmentViewSet, basename='task-attachments')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(tasks_router.urls)),
]
```

### 10.4 Analytics URLs (analytics/urls.py)

```python
"""Analytics URLs."""
from django.urls import path
from .views import (
    OverviewStatsView,
    DailyStatsView,
    WeeklyStatsView,
    ProductivityTrendView,
    CategoryStatsView,
)

urlpatterns = [
    path('overview/', OverviewStatsView.as_view(), name='overview_stats'),
    path('daily/', DailyStatsView.as_view(), name='daily_stats'),
    path('weekly/', WeeklyStatsView.as_view(), name='weekly_stats'),
    path('trends/', ProductivityTrendView.as_view(), name='productivity_trends'),
    path('categories/', CategoryStatsView.as_view(), name='category_stats'),
]
```

---

## 11. Authentication

### 11.1 JWT Token Flow

```
1. User registers → POST /api/v1/auth/register/
   Response: { user, tokens: { access, refresh } }

2. User logs in → POST /api/v1/auth/login/
   Request: { email, password }
   Response: { access, refresh, user }

3. Access protected routes → Include header:
   Authorization: Bearer <access_token>

4. Token expires → POST /api/v1/auth/token/refresh/
   Request: { refresh }
   Response: { access, refresh }  # New tokens

5. User logs out → POST /api/v1/auth/logout/
   Request: { refresh }
   Result: Refresh token blacklisted
```

### 11.2 Frontend Token Storage

```javascript
// Store tokens securely
const storeTokens = (tokens) => {
  // Access token: memory or short-lived storage
  sessionStorage.setItem('access_token', tokens.access);
  // Refresh token: httpOnly cookie (ideal) or localStorage
  localStorage.setItem('refresh_token', tokens.refresh);
};

// API client with auto-refresh
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
});

api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Try to refresh token
      const refresh = localStorage.getItem('refresh_token');
      if (refresh) {
        const response = await axios.post('/api/v1/auth/token/refresh/', { refresh });
        storeTokens(response.data);
        error.config.headers.Authorization = `Bearer ${response.data.access}`;
        return axios(error.config);
      }
    }
    return Promise.reject(error);
  }
);
```

---

## 12. Permissions

### 12.1 Custom Permissions (core/permissions.py)

```python
"""
Custom permissions for Acta.
"""
from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Object-level permission to only allow owners to access their objects."""
    
    def has_object_permission(self, request, view, obj):
        # Check if object has 'user' attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        # Check if object has 'owner' attribute
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allow read access to all, write access only to owner."""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class IsAdminUser(permissions.BasePermission):
    """Allow access only to admin users."""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.roles.filter(role='admin').exists()
        )
```

### 12.2 Applying Permissions

```python
# In views
from core.permissions import IsOwner

class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    
    # Or per-action permissions
    def get_permissions(self):
        if self.action in ['list', 'create']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsOwner()]
```

---

## 13. Filters & Search

### 13.1 Task Filters (tasks/filters.py)

```python
"""
Filters for tasks.
"""
import django_filters
from .models import Task


class TaskFilter(django_filters.FilterSet):
    """Filter for tasks."""
    
    # Exact matches
    status = django_filters.ChoiceFilter(choices=Task.Status.choices)
    priority = django_filters.ChoiceFilter(choices=Task.Priority.choices)
    category = django_filters.UUIDFilter(field_name='category__id')
    
    # Date filters
    due_date = django_filters.DateFilter()
    due_date__gte = django_filters.DateFilter(field_name='due_date', lookup_expr='gte')
    due_date__lte = django_filters.DateFilter(field_name='due_date', lookup_expr='lte')
    created_at__gte = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at__lte = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    
    # Boolean filters
    is_overdue = django_filters.BooleanFilter(method='filter_is_overdue')
    is_due_today = django_filters.BooleanFilter(method='filter_is_due_today')
    
    class Meta:
        model = Task
        fields = ['status', 'priority', 'category', 'due_date']
    
    def filter_is_overdue(self, queryset, name, value):
        from django.utils import timezone
        today = timezone.now().date()
        if value:
            return queryset.filter(
                due_date__lt=today,
                status__in=[Task.Status.PENDING, Task.Status.IN_PROGRESS]
            )
        return queryset.exclude(
            due_date__lt=today,
            status__in=[Task.Status.PENDING, Task.Status.IN_PROGRESS]
        )
    
    def filter_is_due_today(self, queryset, name, value):
        from django.utils import timezone
        today = timezone.now().date()
        if value:
            return queryset.filter(due_date=today)
        return queryset.exclude(due_date=today)
```

---

## 14. Signals

### 14.1 Account Signals (accounts/signals.py)

```python
"""
Signals for accounts app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Profile, UserRole


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a profile when a new user is created."""
    if created:
        Profile.objects.create(user=instance)
        # Assign default user role
        UserRole.objects.create(user=instance, role=UserRole.RoleType.USER)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    """Save profile when user is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()
```

### 14.2 Task Signals (tasks/signals.py)

```python
"""
Signals for tasks app.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Task


@receiver(pre_save, sender=Task)
def handle_task_completion(sender, instance, **kwargs):
    """Handle task status changes."""
    if instance.pk:
        try:
            old_task = Task.objects.get(pk=instance.pk)
            # Task just completed
            if old_task.status != Task.Status.COMPLETED and instance.status == Task.Status.COMPLETED:
                instance.completed_at = timezone.now()
            # Task uncompleted
            elif old_task.status == Task.Status.COMPLETED and instance.status != Task.Status.COMPLETED:
                instance.completed_at = None
        except Task.DoesNotExist:
            pass


@receiver(post_save, sender=Task)
def update_analytics_on_task_change(sender, instance, created, **kwargs):
    """Update analytics when tasks are created or completed."""
    from analytics.models import DailyStats
    
    today = timezone.now().date()
    daily_stats, _ = DailyStats.objects.get_or_create(
        user=instance.user,
        date=today
    )
    
    if created:
        daily_stats.tasks_created += 1
        daily_stats.save()
```

### 14.3 Register Signals (apps.py)

```python
# accounts/apps.py
from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    
    def ready(self):
        import accounts.signals  # noqa

# tasks/apps.py
from django.apps import AppConfig

class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'
    
    def ready(self):
        import tasks.signals  # noqa
```

---

## 15. Management Commands

### 15.1 Create Default Categories (tasks/management/commands/create_default_categories.py)

```python
"""
Management command to create default categories for all users.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tasks.models import Category

User = get_user_model()

DEFAULT_CATEGORIES = [
    {'name': 'Work', 'color': '#3b82f6', 'icon': 'briefcase'},
    {'name': 'Personal', 'color': '#10b981', 'icon': 'user'},
    {'name': 'Health', 'color': '#ef4444', 'icon': 'heart'},
    {'name': 'Learning', 'color': '#8b5cf6', 'icon': 'book'},
    {'name': 'Finance', 'color': '#f59e0b', 'icon': 'dollar'},
]


class Command(BaseCommand):
    help = 'Create default categories for all users'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Create categories for specific user email',
        )
    
    def handle(self, *args, **options):
        user_email = options.get('user')
        
        if user_email:
            users = User.objects.filter(email=user_email)
        else:
            users = User.objects.all()
        
        for user in users:
            for cat_data in DEFAULT_CATEGORIES:
                Category.objects.get_or_create(
                    user=user,
                    name=cat_data['name'],
                    defaults={
                        'color': cat_data['color'],
                        'icon': cat_data['icon'],
                        'is_default': True,
                    }
                )
            self.stdout.write(f'Created categories for {user.email}')
        
        self.stdout.write(self.style.SUCCESS('Default categories created successfully'))
```

### 15.2 Calculate Analytics (analytics/management/commands/calculate_analytics.py)

```python
"""
Management command to calculate daily/weekly analytics.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from tasks.models import Task
from analytics.models import DailyStats, WeeklyStats

User = get_user_model()


class Command(BaseCommand):
    help = 'Calculate analytics for all users'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Calculate for specific date (YYYY-MM-DD)',
        )
    
    def handle(self, *args, **options):
        date_str = options.get('date')
        target_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else timezone.now().date()
        
        for user in User.objects.all():
            # Daily stats
            daily_stats, _ = DailyStats.objects.get_or_create(
                user=user,
                date=target_date
            )
            
            tasks = Task.objects.filter(user=user)
            daily_stats.tasks_created = tasks.filter(created_at__date=target_date).count()
            daily_stats.tasks_completed = tasks.filter(
                status=Task.Status.COMPLETED,
                completed_at__date=target_date
            ).count()
            daily_stats.tasks_overdue = tasks.filter(
                due_date__lt=target_date,
                status__in=[Task.Status.PENDING, Task.Status.IN_PROGRESS]
            ).count()
            daily_stats.save()
            
            self.stdout.write(f'Updated daily stats for {user.email}')
        
        self.stdout.write(self.style.SUCCESS('Analytics calculated successfully'))
```

---

## 16. Testing

### 16.1 Test Configuration (conftest.py)

```python
"""
Pytest configuration and fixtures.
"""
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def api_client():
    """Return an API client instance."""
    return APIClient()


@pytest.fixture
def user(db):
    """Create and return a test user."""
    return User.objects.create_user(
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """Return an authenticated API client."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def task(user):
    """Create and return a test task."""
    from tasks.models import Task
    return Task.objects.create(
        user=user,
        title='Test Task',
        description='Test description',
        priority=Task.Priority.MEDIUM,
        status=Task.Status.PENDING
    )
```

### 16.2 Task Tests (tasks/tests/test_views.py)

```python
"""
Tests for task views.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from tasks.models import Task


@pytest.mark.django_db
class TestTaskViewSet:
    """Tests for TaskViewSet."""
    
    def test_list_tasks(self, authenticated_client, task):
        """Test listing tasks."""
        url = reverse('task-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
    
    def test_create_task(self, authenticated_client):
        """Test creating a task."""
        url = reverse('task-list')
        data = {
            'title': 'New Task',
            'description': 'Task description',
            'priority': 'high',
            'status': 'pending'
        }
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Task.objects.filter(title='New Task').exists()
    
    def test_update_task(self, authenticated_client, task):
        """Test updating a task."""
        url = reverse('task-detail', kwargs={'pk': task.id})
        data = {'title': 'Updated Task'}
        response = authenticated_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.title == 'Updated Task'
    
    def test_delete_task(self, authenticated_client, task):
        """Test deleting a task."""
        url = reverse('task-detail', kwargs={'pk': task.id})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Task.objects.filter(id=task.id).exists()
    
    def test_toggle_complete(self, authenticated_client, task):
        """Test toggling task completion."""
        url = reverse('task-toggle-complete', kwargs={'pk': task.id})
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.status == Task.Status.COMPLETED
    
    def test_unauthorized_access(self, api_client):
        """Test that unauthenticated requests are rejected."""
        url = reverse('task-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

### 16.3 Running Tests

```bash
# Install pytest
pip install pytest pytest-django

# Create pytest.ini
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = Acta_backend.settings.development
python_files = tests.py test_*.py *_tests.py

# Run tests
pytest

# Run with coverage
pip install pytest-cov
pytest --cov=. --cov-report=html
```

---

## 17. Deployment

### 17.1 Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "Acta_backend.wsgi:application"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=postgres://postgres:postgres@db:5432/Acta
    depends_on:
      - db
      - redis
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
  
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=Acta
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
  
  redis:
    image: redis:7-alpine
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - web

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

### 17.2 Production Checklist

```bash
# 1. Set environment variables
export DEBUG=False
export SECRET_KEY=<strong-random-key>
export ALLOWED_HOSTS=yourdomain.com

# 2. Run migrations
python manage.py migrate

# 3. Create superuser
python manage.py createsuperuser

# 4. Collect static files
python manage.py collectstatic

# 5. Run with gunicorn
pip install gunicorn
gunicorn Acta_backend.wsgi:application --bind 0.0.0.0:8000
```

---

## 18. Frontend Integration

### 18.1 API Client Setup (React/TypeScript)

```typescript
// src/lib/api-client.ts
import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor - handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && originalRequest) {
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken,
          });
          
          const { access, refresh } = response.data;
          localStorage.setItem('access_token', access);
          localStorage.setItem('refresh_token', refresh);
          
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed - logout user
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/auth/signin';
      }
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
```

### 18.2 Type Definitions

```typescript
// src/types/api.ts
export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  initials: string;
  avatar?: string;
}

export interface Task {
  id: string;
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  due_date: string | null;
  due_time: string | null;
  category: Category | null;
  category_id?: string;
  is_overdue: boolean;
  is_due_today: boolean;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

export interface Category {
  id: string;
  name: string;
  color: string;
  icon: string;
  task_count: number;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
}
```

### 18.3 API Service Functions

```typescript
// src/services/task-service.ts
import apiClient from '@/lib/api-client';
import type { Task, PaginatedResponse } from '@/types/api';

export const taskService = {
  // List tasks with filters
  async getTasks(params?: {
    status?: string;
    priority?: string;
    category?: string;
    search?: string;
    ordering?: string;
    page?: number;
  }): Promise<PaginatedResponse<Task>> {
    const response = await apiClient.get('/tasks/', { params });
    return response.data;
  },
  
  // Get single task
  async getTask(id: string): Promise<Task> {
    const response = await apiClient.get(`/tasks/${id}/`);
    return response.data;
  },
  
  // Create task
  async createTask(data: Partial<Task>): Promise<Task> {
    const response = await apiClient.post('/tasks/', data);
    return response.data;
  },
  
  // Update task
  async updateTask(id: string, data: Partial<Task>): Promise<Task> {
    const response = await apiClient.patch(`/tasks/${id}/`, data);
    return response.data;
  },
  
  // Delete task
  async deleteTask(id: string): Promise<void> {
    await apiClient.delete(`/tasks/${id}/`);
  },
  
  // Toggle completion
  async toggleComplete(id: string): Promise<Task> {
    const response = await apiClient.post(`/tasks/${id}/toggle_complete/`);
    return response.data;
  },
  
  // Get tasks due today
  async getTodayTasks(): Promise<Task[]> {
    const response = await apiClient.get('/tasks/today/');
    return response.data;
  },
  
  // Get completed tasks (last 7 days)
  async getCompletedTasks(): Promise<Task[]> {
    const response = await apiClient.get('/tasks/completed/');
    return response.data;
  },
};
```

### 18.4 React Query Hooks

```typescript
// src/hooks/use-tasks.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { taskService } from '@/services/task-service';
import { toast } from 'sonner';

export function useTasks(params?: Parameters<typeof taskService.getTasks>[0]) {
  return useQuery({
    queryKey: ['tasks', params],
    queryFn: () => taskService.getTasks(params),
  });
}

export function useTask(id: string) {
  return useQuery({
    queryKey: ['task', id],
    queryFn: () => taskService.getTask(id),
    enabled: !!id,
  });
}

export function useCreateTask() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: taskService.createTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      toast.success('Task created successfully');
    },
    onError: () => {
      toast.error('Failed to create task');
    },
  });
}

export function useUpdateTask() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Task> }) =>
      taskService.updateTask(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      toast.success('Task updated');
    },
  });
}

export function useToggleComplete() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: taskService.toggleComplete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
}
```

---

## Summary

This document provides a complete blueprint for building the Acta Django backend, including:

- ✅ Full project structure and configuration
- ✅ Database models with relationships
- ✅ REST API serializers for all entities
- ✅ ViewSets and views with filtering
- ✅ Complete API endpoint reference
- ✅ JWT authentication setup
- ✅ Custom permissions
- ✅ Signals for automation
- ✅ Management commands
- ✅ Testing configuration
- ✅ Docker deployment setup
- ✅ Frontend integration guide

**Next Steps:**
1. Set up the Django project following this guide
2. Create models and run migrations
3. Implement serializers and views
4. Configure authentication
5. Update frontend to use the API
6. Deploy to production

---

*Document Version: 1.0*  
*Last Updated: January 2026*
