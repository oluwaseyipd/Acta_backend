# Acta Backend

A modern, production-ready Django REST API backend for task management and productivity tracking. Built with Django REST Framework and JWT authentication.

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Authentication](#-authentication)
- [Testing](#-testing)
- [Database](#-database)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

- **User Authentication & Authorization**
  - JWT-based authentication with refresh tokens
  - Email-based user registration and login
  - Role-based access control
  - Password reset and change functionality
  - Token blacklisting for secure logout

- **Task Management**
  - Create, read, update, and delete tasks
  - Task categorization
  - Priority levels and status tracking
  - Task assignment and collaboration
  - Task comments and attachments
  - Bulk task operations
  - Advanced filtering and search

- **User Profiles**
  - Customizable user profiles
  - Avatar upload support
  - Contact information management
  - Timezone and preference settings
  - Notification preferences

- **Analytics**
  - Task completion analytics
  - Performance metrics
  - Automated analytics calculation
  - Data cleanup utilities

- **API Features**
  - RESTful API design
  - Pagination support
  - Advanced filtering (DjangoFilterBackend)
  - Full-text search capabilities
  - CORS enabled for frontend integration
  - Comprehensive error handling

## 🛠 Tech Stack

- **Backend Framework**: Django 4.2+
- **API Framework**: Django REST Framework
- **Authentication**: Django REST Framework SimpleJWT & Google OAuth2
- **Database**: SQLite (development) / PostgreSQL (production)
- **Task Queue & Broker**: Celery & Redis
- **Object Storage (Media)**: Cloudflare R2 (S3-compatible) via `django-storages[s3]`
- **Process Manager**: Supervisor (`supervisord` to run Gunicorn + Celery in a single container)
- **Static Files**: WhiteNoise
- **CORS**: django-cors-headers
- **Filtering**: django-filter
- **Testing**: pytest, pytest-django
- **Environment Management**: python-decouple
- **Containerization**: Docker & Docker Compose
- **Deployment Blueprint**: Render Blueprint (`render.yaml`)

## 📦 Installation

### Prerequisites

- Python 3.8+
- pip or pipenv
- Virtual environment (recommended)

### Clone the Repository

```bash
git clone https://github.com/yourusername/acta-backend.git
cd acta-backend
```

### Create Virtual Environment

```bash
# Using venv
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### Install Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Or using pipenv
pipenv install
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development

# Database
DATABASE_URL=sqlite:///db.sqlite3

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Email Configuration (for password reset)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password

# Redis & Celery Settings
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Object Storage Configuration (Cloudflare R2/S3 - Production)
USE_S3=False
AWS_ACCESS_KEY_ID=your-cloudflare-r2-access-key
AWS_SECRET_ACCESS_KEY=your-cloudflare-r2-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_ENDPOINT_URL=https://<account_id>.r2.cloudflarestorage.com
AWS_S3_CUSTOM_DOMAIN=media.yourdomain.com

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=https://your-frontend.com/auth/google/callback
```

### Settings Modules

The project uses environment-specific settings:

- `settings/base.py` - Common settings
- `settings/development.py` - Development environment
- `settings/production.py` - Production environment

Set the Django settings module:

```bash
# Development (default)
export DJANGO_SETTINGS_MODULE=Acta_backend.settings.development

# Production
export DJANGO_SETTINGS_MODULE=Acta_backend.settings.production
```

## 🚀 Running the Application

### Database Migration

```bash
python manage.py migrate
```

### Create Superuser

```bash
python manage.py createsuperuser --email admin@example.com
```

### Run Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/v1/`

### Collect Static Files

```bash
python manage.py collectstatic --noinput
```

## 📚 API Documentation

### Base URL

```
http://localhost:8000/api/v1/
```

### Authentication Endpoints

#### Register User

```
POST /auth/register/

Request:
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "securepassword123",
  "password_confirm": "securepassword123"
}

Response:
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "tokens": {
    "refresh": "refresh_token",
    "access": "access_token"
  },
  "message": "Registration successful"
}
```

#### Login

```
POST /auth/login/

Request:
{
  "email": "user@example.com",
  "password": "securepassword123"
}

Response:
{
  "refresh": "refresh_token",
  "access": "access_token",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe"
  }
}
```

#### Refresh Token

```
POST /auth/token/refresh/

Request:
{
  "refresh": "refresh_token"
}

Response:
{
  "access": "new_access_token"
}
```

#### Logout

```
POST /auth/logout/

Request:
{
  "refresh": "refresh_token"
}

Response:
{
  "message": "Logout successful"
}
```

#### Change Password

```
PUT /auth/password/change/

Authorization: Bearer <access_token>

Request:
{
  "old_password": "current_password",
  "new_password": "new_password",
  "new_password_confirm": "new_password"
}

Response:
{
  "message": "Password changed successfully"
}
```

### User Profile Endpoints

#### Get Current User Profile

```
GET /users/profile/

Authorization: Bearer <access_token>

Response:
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "phone_number": "+1234567890",
  "bio": "User bio",
  "location": "City, Country",
  "birth_date": "1990-01-01",
  "avatar": "url_to_avatar",
  "website": "https://example.com",
  "timezone": "UTC",
  "notification_preferences": {},
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Update User Profile

```
PUT /users/profile/

Authorization: Bearer <access_token>
Content-Type: multipart/form-data

Request (form data):
first_name: "John"
last_name": "Updated"
phone_number: "+1234567890"
bio: "Updated bio"
avatar: <file>

Response: Updated profile object
```

### Task Endpoints

#### List Tasks

```
GET /tasks/?status=pending&priority=high&search=important

Authorization: Bearer <access_token>

Query Parameters:
- status: pending, in_progress, completed, cancelled
- priority: low, medium, high, urgent
- search: search term for title/description
- ordering: created_at, due_date, priority, status
- page: page number

Response:
{
  "count": 42,
  "next": "http://localhost:8000/api/v1/tasks/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "title": "Task Title",
      "description": "Task description",
      "status": "pending",
      "priority": "high",
      "due_date": "2024-02-28T23:59:59Z",
      "category": "category_id",
      "assigned_to": "user_uuid",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Create Task

```
POST /tasks/

Authorization: Bearer <access_token>

Request:
{
  "title": "New Task",
  "description": "Task description",
  "priority": "high",
  "status": "pending",
  "due_date": "2024-02-28T23:59:59Z",
  "category": "category_id",
  "assigned_to": "user_uuid"
}

Response: Created task object
```

#### Get Task Details

```
GET /tasks/{id}/

Authorization: Bearer <access_token>

Response: Full task object with comments and attachments
```

#### Update Task

```
PATCH /tasks/{id}/

Authorization: Bearer <access_token>

Request: Task fields to update

Response: Updated task object
```

#### Delete Task

```
DELETE /tasks/{id}/

Authorization: Bearer <access_token>

Response: 204 No Content
```

#### Task Comments

```
POST /tasks/{id}/comments/

Authorization: Bearer <access_token>

Request:
{
  "content": "Comment text"
}
```

#### Task Attachments

```
POST /tasks/{id}/attachments/

Authorization: Bearer <access_token>
Content-Type: multipart/form-data

Request:
file: <file>
```

### Analytics Endpoints

#### Get Analytics

```
GET /analytics/?date_range=30&metric_type=completion_rate

Authorization: Bearer <access_token>

Response:
{
  "total_tasks": 50,
  "completed_tasks": 30,
  "pending_tasks": 20,
  "completion_rate": 60,
  "tasks_by_priority": {...},
  "tasks_by_status": {...}
}
```

## 🔐 Authentication

All API endpoints (except registration and login) require JWT authentication.

### Using the API

1. **Register/Login** to get tokens
2. **Include access token** in request header:
   ```
   Authorization: Bearer <access_token>
   ```
3. **Use refresh token** to get new access token when expired
4. **Logout** to blacklist refresh token and end session

### Token Details

- **Access Token**: Valid for 60 minutes (configurable)
- **Refresh Token**: Valid for 24 hours (configurable)
- **Token Rotation**: Refresh tokens rotate on use for enhanced security
- **Blacklist**: Tokens are blacklisted on logout

## 📁 Project Structure

```
acta-backend/
├── Acta_backend/              # Main project settings
│   ├── settings/
│   │   ├── base.py           # Common settings
│   │   ├── development.py    # Development settings
│   │   └── production.py     # Production settings
│   ├── urls.py               # Main URL configuration
│   ├── wsgi.py               # WSGI configuration
│   └── asgi.py               # ASGI configuration
│
├── accounts/                  # User authentication app
│   ├── models.py             # Custom User model
│   ├── views.py              # Auth views
│   ├── serializers.py        # Auth serializers
│   ├── signals.py            # User signals
│   ├── urls/
│   │   ├── auth_urls.py      # Authentication endpoints
│   │   └── user_urls.py      # User profile endpoints
│   ├── migrations/
│   └── tests.py              # Auth tests
│
├── tasks/                     # Task management app
│   ├── models.py             # Task, Category, Comment, Attachment models
│   ├── views.py              # Task views/viewsets
│   ├── serializers.py        # Task serializers
│   ├── filters.py            # Task filters
│   ├── urls.py               # Task endpoints
│   ├── management/
│   │   └── commands/         # Custom management commands
│   ├── migrations/
│   └── tests.py              # Task tests
│
├── analytics/                 # Analytics app
│   ├── models.py             # Analytics models
│   ├── views.py              # Analytics views
│   ├── serializers.py        # Analytics serializers
│   ├── urls.py               # Analytics endpoints
│   ├── management/
│   │   └── commands/
│   │       ├── calculate_analytics.py
│   │       └── cleanup_analytics.py
│   ├── migrations/
│   └── tests.py              # Analytics tests
│
├── core/                      # Core utilities
│   ├── permissions.py        # Custom permissions
│   ├── views.py              # Core views
│   └── models.py             # Core models
│
├── tests/                     # Integration tests
│   ├── test_accounts.py
│   ├── test_tasks.py
│   └── test_analytics.py
│
├── static/                    # Static files
├── staticfiles/               # Compiled static files
├── media/                     # User uploads
├── templates/                 # Email templates
│
├── manage.py                  # Django management script
├── requirements.txt           # Python dependencies
├── Pipfile                    # Pipenv dependencies
├── pytest.ini                 # Pytest configuration
├── conftest.py               # Pytest fixtures
├── db.sqlite3                # SQLite database (dev only)
├── .env                      # Environment variables (not in git)
└── README.md                 # This file
```

## 🧪 Testing

Run tests using pytest:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_accounts.py

# Run with coverage report
pytest --cov=.

# Run only unit tests
pytest -m "not integration"

# Verbose output
pytest -v
```

### Test Configuration

Configuration is in `pytest.ini` and `conftest.py`:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = Acta_backend.settings.development
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

### Test Files

- `tests/test_accounts.py` - Authentication and user tests
- `tests/test_tasks.py` - Task management tests
- `tests/test_analytics.py` - Analytics tests
- Individual app `tests.py` files for unit tests

## 🗄️ Database

### Models

#### User Model (`accounts`)
- UUID primary key
- Email-based authentication
- First & last name
- Active status and timestamps

#### Profile Model (`accounts`)
- One-to-one with User
- Avatar, bio, location
- Contact information
- Timezone and preferences

#### Task Model (`tasks`)
- Title, description, priority
- Status tracking
- Due date and timestamps
- Category and assignment
- Owner tracking

#### Category Model (`tasks`)
- Category name and description
- Color coding

#### TaskComment Model (`tasks`)
- Comments on tasks
- Author and timestamp

#### TaskAttachment Model (`tasks`)
- File attachments
- File metadata

#### Analytics Model (`analytics`)
- Metrics and statistics
- Date-based records

### Migrations

Apply migrations:

```bash
# Apply all migrations
python manage.py migrate

# Create migration for changes
python manage.py makemigrations

# See migration status
python manage.py showmigrations
```

## 🚢 Deployment

### Local Container Deployment (Docker & Compose)

We provide a complete Docker configuration to run the application locally inside containerized environments:

1. **Build and start the services:**
   ```bash
   docker-compose up --build -d
   ```
   This orchestrates three containers:
   - `acta_postgres`: Running PostgreSQL 16 database.
   - `acta_redis`: Running Redis 7 message broker/cache.
   - `acta_web`: Running the Django application with `supervisord` executing Gunicorn and Celery background workers.

2. **Run database migrations manually (if needed):**
   The container runs migrations and collects static files automatically on startup via the `docker-entrypoint.sh` hook. If you need to run them manually:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. **Stop the services:**
   ```bash
   docker-compose down
   ```

### Production Deployment via Render (Blueprint)

This project has been pre-configured with a Render Blueprint [render.yaml](file:///d:/OVERSIGHT/Acta_backend/render.yaml) for instant cloud deployments:

1. Push your code to your GitHub repository.
2. Go to the **Render Dashboard** -> **New** -> **Blueprint**.
3. Select this repository.
4. Render will parse `render.yaml` and provision:
   - A managed PostgreSQL database.
   - An internal Redis cache.
   - A Docker-based Web Service (builds the image, applies database migrations, collects static assets, and boots both Gunicorn and Celery workers inside supervisor).
5. Provide the required S3/R2 and Google OAuth variables in Render's configuration prompts (or under the environment variables settings tab):
   - `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`, `AWS_S3_ENDPOINT_URL`
   - `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`
6. Click **Apply** and wait for deployment to complete.

### Environment-Specific Settings

When running outside of Docker locally:
```bash
# Development (uses SQLite)
export DJANGO_SETTINGS_MODULE=Acta_backend.settings.development

# Production (uses PostgreSQL and R2 S3 storage)
export DJANGO_SETTINGS_MODULE=Acta_backend.settings.production
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8
- Use meaningful variable/function names
- Add docstrings to functions and classes
- Write tests for new features
- Update documentation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 📞 Support

For support, email support@example.com or open an issue on GitHub.

## 🔗 Links

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/)
- [API Design Best Practices](https://restfulapi.net/)

---

**Last Updated**: February 2026
