# Acta Backend - Technical Knowledge Document

This document provides a comprehensive overview of the `Acta_backend` architecture, database models, permissions structure, API catalog, background Celery tasks, and deployment configurations. Use this to verify alignment with the frontend service layer (`acta-frontend`).

---

## 1. System Architecture & Tech Stack

*   **Language & Core Framework:** Python 3.12, Django 4.2.28
*   **Web Services API:** Django REST Framework (DRF) 3.16.1
*   **Authentication:** SimpleJWT (JWT Bearer token-based auth)
*   **Database:** PostgreSQL (Production on Render) / SQLite (Local Development)
*   **Task Queue & Caching:** Celery 5.6.2 & Redis (Celery fallback is `redis://localhost:6379/0` if `REDIS_URL` is not provided)
*   **Email Engine:** Custom Resend REST API Backend (`ResendEmailBackend`) with HTML email templates, falling back to python console logging in development
*   **WSGI Web Server:** Gunicorn 25.1.0 (binds dynamically to `$PORT` environment variable)
*   **Process Supervisor:** Supervisor (Supervisord) 4.3.0 to manage Gunicorn and Celery worker processes inside a single instance

---

## 2. Environment Variables (`.env`)

These environment variables configure the application settings dynamically:

| Env Variable Name | Type | Description / Default Value |
| :--- | :--- | :--- |
| `DJANGO_SECRET_KEY` / `SECRET_KEY` | String | Django secret key for cryptographic signing |
| `DEBUG` | Boolean | Development debug mode toggle. Defaults to `False` in prod |
| `DJANGO_SETTINGS_MODULE` | String | Django settings path. `Acta_backend.settings.production` or `.development` |
| `DATABASE_URL` / `DB_URL` | String | Database connection string. Automatically injected by Render |
| `REDIS_URL` | String | Connection string for Redis. Used for Celery brokers |
| `RESEND_API_KEY` | String | API token from Resend dashboard. Enables transactional email |
| `DEFAULT_FROM_EMAIL` | String | Outgoing mail sender address (e.g. `no-reply@hgbcinfluencers.org`) |
| `EMAIL_FROM_NAME` | String | Sender name branding (e.g. `"Team Acta"`) |
| `FRONTEND_ORIGIN` / `FRONTEND_URL` | String | Frontend URL path for CORS origins and email links (e.g. `https://acta-psi.vercel.app`) |
| `CORS_ALLOWED_ORIGINS` | Commas | Allowed origins for CORS (e.g. `https://acta-psi.vercel.app,http://localhost:3000`) |
| `ALLOWED_HOSTS` | Commas | Host headers allowed by Django (e.g. `acta-backend-vcbr.onrender.com,localhost`) |
| `GOOGLE_CLIENT_ID` | String | OAuth2 Client ID from Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | String | OAuth2 Client Secret from Google Cloud Console |
| `GOOGLE_REDIRECT_URI` | String | Redirect endpoint configured in Google Cloud (e.g., `https://acta-psi.vercel.app/auth/google/callback`) |

---

## 3. Database Schema & Models

### A. Accounts Component

#### `User` (Extends `AbstractUser`)
*   **Table name:** `accounts_user`
*   **Fields:**
    *   `id` (UUIDField, Primary Key, Auto-gen)
    *   `email` (EmailField, Unique, Used as Username)
    *   `first_name` (CharField, max 30)
    *   `last_name` (CharField, max 30)
    *   `is_active` (BooleanField, default: `True`)
    *   `is_staff` (BooleanField, default: `False`)
    *   `date_joined` (DateTimeField, auto)
    *   `last_login` (DateTimeField, optional)
*   **Properties/Methods:**
    *   `full_name` -> Returns `"First Last"`
    *   `get_initials()` -> Returns upper initials (e.g., `"JD"`)

#### `Profile`
*   **Table name:** `accounts_profile`
*   **Fields:**
    *   `user` (OneToOneField on `User`, related name: `profile`)
    *   `phone_number` (CharField, regex validated `+999999999` up to 15 digits)
    *   `bio` (TextField, max 500)
    *   `location` (CharField, max 100)
    *   `birth_date` (DateField, optional)
    *   `avatar` (ImageField, uploads to Cloudinary storage via dynamic settings in production)
    *   `website` (URLField)
    *   `timezone` (CharField, default: `'UTC'`)
    *   `notification_preferences` (JSONField, default: `dict`)
    *   `created_at` / `updated_at` (DateTimeFields)

#### `PasswordResetToken`
*   **Table name:** `accounts_password_reset_token`
*   **Fields:**
    *   `id` (UUIDField, Primary Key)
    *   `token` (CharField, default: random UUID)
    *   `user` (ForeignKey on `User`)
    *   `created_at` (DateTimeField, auto)
    *   `is_used` (BooleanField, default: `False`)

---

### B. Tasks Component

#### `Category`
*   **Table name:** `tasks_category`
*   **Fields:**
    *   `id` (UUIDField, Primary Key)
    *   `name` (CharField, max 100)
    *   `description` (TextField)
    *   `color` (CharField, Hex Code, default: `#3B82F6`)
    *   `icon` (CharField, max 50)
    *   `user` (ForeignKey on `User`, related name: `categories`)
    *   `is_default` (BooleanField, default: `False`)
    *   `created_at` / `updated_at` (DateTimeFields)
*   **Constraints:**
    *   `unique_together` on `['name', 'user']` (case-insensitive validation in serializers)

#### `Task`
*   **Table name:** `tasks_task`
*   **Fields:**
    *   `id` (UUIDField, Primary Key)
    *   `title` (CharField, max 200)
    *   `description` (TextField)
    *   `status` (CharField choices: `pending`, `in_progress`, `completed`, `cancelled`)
    *   `priority` (CharField choices: `low`, `medium`, `high`, `urgent`)
    *   `category` (ForeignKey on `Category`, nullable, related name: `tasks`)
    *   `user` (ForeignKey on `User`, related name: `tasks`)
    *   `assigned_to` (ForeignKey on `User`, nullable, related name: `assigned_tasks`)
    *   `due_date` / `start_date` (DateTimeFields)
    *   `estimated_hours` / `actual_hours` (DecimalFields, `max_digits=5`, `decimal_places=2`)
    *   `created_at` / `updated_at` (DateTimeFields)

#### `TaskComment`
*   **Table name:** `tasks_comment`
*   **Fields:**
    *   `id` (UUIDField, Primary Key)
    *   `task` (ForeignKey on `Task`, related name: `comments`)
    *   `user` (ForeignKey on `User`, related name: `task_comments`)
    *   `content` (TextField)
    *   `created_at` / `updated_at` (DateTimeFields)

#### `TaskAttachment`
*   **Table name:** `tasks_attachment`
*   **Fields:**
    *   `id` (UUIDField, Primary Key)
    *   `task` (ForeignKey on `Task`, related name: `attachments`)
    *   `file` (FileField, uploads to MediaCloudinaryStorage)
    *   `file_name` (CharField, max 255)
    *   `uploaded_at` (DateTimeField)

---

### C. Analytics Component

#### `DailyStats`
*   **Table name:** `analytics_daily_stats`
*   **Fields:**
    *   `id` (UUIDField, Primary Key)
    *   `date` (DateField)
    *   `user` (ForeignKey on `User`, related name: `daily_stats`)
    *   `total_tasks` (IntegerField)
    *   `completed_tasks` (IntegerField)
    *   `completion_rate` (DecimalField)
    *   `total_estimated_hours` / `total_actual_hours` (DecimalFields)

#### `WeeklyStats`
*   **Table name:** `analytics_weekly_stats`
*   **Fields:**
    *   `id` (UUIDField, Primary Key)
    *   `week_start` (DateField)
    *   `user` (ForeignKey on `User`, related name: `weekly_stats`)
    *   `total_tasks` (IntegerField)
    *   `completed_tasks` (IntegerField)
    *   `completion_rate` (DecimalField)
    *   `total_estimated_hours` / `total_actual_hours` (DecimalFields)

---

## 4. API Endpoint Catalog

All routes are versioned and prefixed with `/api/v1/`. All endpoints except registration, login, token refresh, Google auth URL, Google callback, and password reset requests/confirms require a JWT token in the `Authorization` header (`Bearer <access_token>`).

### A. Authentication & SSO (`/api/v1/auth/`)

| Method | Endpoint | Request Payload | Response Schema (Success) |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/register/` | `{ first_name, last_name, email, password, password_confirm }` | User profile & JWT tokens: `{ user: {...}, access, refresh }` |
| `POST` | `/auth/login/` | `{ email, password }` | JWT Auth tokens: `{ user: {...}, access, refresh }` |
| `POST` | `/auth/logout/` | `{ refresh }` (refresh token string) | `{ "detail": "Successfully logged out." }` |
| `POST` | `/auth/token/refresh/` | `{ refresh }` (refresh token string) | `{ "access": "..." }` |
| `POST` | `/auth/password/change/` | `{ old_password, new_password, new_password_confirm }` | `{ "message": "Password changed successfully." }` |
| `POST` | `/auth/password/reset/` | `{ email }` | `{ "message": "Password reset link sent to email." }` |
| `POST` | `/auth/password/reset/confirm/` | `{ token, new_password, new_password_confirm }` | `{ "message": "Password has been reset successfully." }` |
| `GET` | `/auth/google/url/` | None | `{ "url": "https://accounts.google.com/o/oauth2/..." }` |
| `POST` | `/auth/google/callback/` | `{ code }` (Google code parameter) | JWT Auth tokens: `{ user: {...}, access, refresh }` |

---

### B. User Details & Profiles (`/api/v1/users/`)

| Method | Endpoint | Request Payload | Response Schema (Success) |
| :--- | :--- | :--- | :--- |
| `GET` | `/users/me/` | None | `{ id, email, first_name, last_name, full_name, get_initials }` |
| `PATCH` | `/users/me/` | `{ email, first_name, last_name }` (partial update) | Updated user object |
| `GET` | `/users/profile/` | None | `{ phone_number, bio, location, birth_date, avatar, website, timezone, notification_preferences }` |
| `PATCH` | `/users/profile/` | Form data: `{ phone_number, bio, location, avatar (File), website, timezone }` | Updated profile object |

---

### C. Category Management (`/api/v1/categories/`)

| Method | Endpoint | Request Payload | Response Schema (Success) |
| :--- | :--- | :--- | :--- |
| `GET` | `/categories/` | None | List of user's categories |
| `POST` | `/categories/` | `{ name, description, color, icon }` | Created category object |
| `GET` | `/categories/<id>/` | None | Individual category object |
| `PUT` | `/categories/<id>/` | `{ name, description, color, icon }` | Updated category object |
| `PATCH` | `/categories/<id>/` | `{ name, description, color, icon }` (partial) | Updated category object |
| `DELETE` | `/categories/<id>/` | None | `204 No Content` |

---

### D. Task Management (`/api/v1/tasks/`)

| Method | Endpoint | Request Payload | Response Schema (Success) |
| :--- | :--- | :--- | :--- |
| `GET` | `/tasks/` | Query params: `status`, `priority`, `category`, `search`, `ordering` | Paginated task list: `{ count, next, previous, results: [...] }` |
| `POST` | `/tasks/` | `{ title, description, status, priority, category (UUID), due_date, start_date, estimated_hours }` | Created task object |
| `GET` | `/tasks/<id>/` | None | Individual task object |
| `PUT` | `/tasks/<id>/` | Full task fields | Updated task object |
| `PATCH` | `/tasks/<id>/` | Partial task fields | Updated task object |
| `DELETE` | `/tasks/<id>/` | None | `204 No Content` |
| `PATCH` | `/tasks/<id>/toggle-complete/` | None | `{ "status": "completed"/"pending", "message": "..." }` |
| `PATCH` | `/tasks/<id>/update-status/` | `{ status }` | `{ "status": "...", "message": "Status updated successfully" }` |
| `POST` | `/tasks/bulk-complete/` | `{ task_ids: [UUID, ...] }` | `{ "message": "Successfully completed X tasks." }` |
| `POST` | `/tasks/bulk-delete/` | `{ task_ids: [UUID, ...] }` | `{ "message": "Successfully deleted X tasks." }` |

---

### E. Task Comments & Attachments (`/api/v1/tasks/<id>/`)

| Method | Endpoint | Request Payload | Response Schema (Success) |
| :--- | :--- | :--- | :--- |
| `GET` | `/tasks/<id>/comments/` | None | List of task comments |
| `POST` | `/tasks/<id>/comments/` | `{ content }` | Created comment object |
| `DELETE` | `/tasks/<id>/comments/<cid>/` | None | `204 No Content` |
| `GET` | `/tasks/<id>/attachments/` | None | List of task attachments |
| `POST` | `/tasks/<id>/attachments/` | Form data: `{ file, file_name }` | Created attachment object |
| `DELETE` | `/tasks/<id>/attachments/<aid>/` | None | `204 No Content` |

---

### F. Analytics & Reporting (`/api/v1/analytics/`)

| Method | Endpoint | Request Payload | Response Schema (Success) |
| :--- | :--- | :--- | :--- |
| `GET` | `/analytics/overview/` | None | `{ total_tasks, completed_tasks, pending_tasks, completion_rate, average_estimated_hours, average_actual_hours, overdue_tasks_count }` |
| `GET` | `/analytics/daily-stats/` | Query params: `days` | Paginated list of daily stats |
| `GET` | `/analytics/weekly-stats/` | Query params: `weeks` | Paginated list of weekly stats |
| `GET` | `/analytics/productivity-trends/`| Query params: `days` | Dynamic list of dates aggregated by database counts: `[{ date, created_count, completed_count }]` |
| `GET` | `/analytics/category-stats/` | None | List of stats grouped by categories: `[{ category_id, category_name, color, task_count, completed_count }]` |

---

## 5. Security & Permissions Architecture (`core/permissions.py`)

Permissions enforce security policies across views. Custom permission classes are:

1.  **`IsOwner`:** Matches the `user` or `owner` foreign key attribute of an object with `request.user`.
2.  **`IsOwnerOrReadOnly`:** Allows access to SAFE_METHODS (`GET`, `HEAD`, `OPTIONS`) to all authenticated users, restricting writes to the object owner.
3.  **`IsAdminUser`:** Restricts access to users with `is_superuser=True` or `role='admin'`.
4.  **`IsManagerOrAdmin`:** Restricts access to managers or admin users (used for team task tracking).
5.  **`IsProfileOwnerOrReadOnly`:** Restricts profile writes to the owner.
6.  **`IsTaskOwnerOrAssigned`:** Restricts task editing to the creator, but allows read access and status patching to the assigned user.
7.  **`CanCreateTask`:** Enforces that users with a viewer role cannot create tasks.
8.  **`CanManageUsers`:** Restricts user creation/management to admins.
9.  **`CanViewAnalytics`:** Grants user access to run analytics aggregations.

---

## 6. Background Asynchronous Actions (Celery)

Celery processes long-running workflows asynchronously inside task queries:

*   **Welcome Email Sequence (`send_welcome_email.delay(user_id)`)**: Dispatched after user register signals are executed. Sends an HTML branded onboarding email.
*   **Password Reset Email Request (`send_password_reset_email.delay(user_id, token_str)`)**: Triggered on request reset. Generates a path link with the query string token parameter pointing to the frontend.
*   **Password Changed Email (`send_password_changed_email.delay(user_id)`)**: Triggered after password change view updates.
