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
*   **Media Storage:** Cloudinary Storage (`MediaCloudinaryStorage`) for image avatars and attachments in production
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
| `FRONTEND_URL` | String | Frontend URL path for CORS origins and email links (e.g. `https://acta-psi.vercel.app`) |
| `CORS_ALLOWED_ORIGINS` | Commas | Allowed origins for CORS (e.g. `https://acta-psi.vercel.app,http://localhost:3000`) |
| `ALLOWED_HOSTS` | Commas | Host headers allowed by Django (e.g. `acta-backend-vcbr.onrender.com,localhost`) |
| `GOOGLE_CLIENT_ID` | String | OAuth2 Client ID from Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | String | OAuth2 Client Secret from Google Cloud Console |
| `GOOGLE_REDIRECT_URI` | String | Redirect endpoint configured in Google Cloud (e.g., `https://acta-psi.vercel.app/auth/google/callback`) |
| `CLOUDINARY_CLOUD_NAME` | String | Cloudinary cloud identifier for media storage |
| `CLOUDINARY_API_KEY` | String | Cloudinary access API key |
| `CLOUDINARY_API_SECRET` | String | Cloudinary access API secret |
| `MAX_UPLOAD_SIZE` | Integer| Maximum file upload limit in bytes. Default: `5242880` (5 MB) |

---

## 3. Database Schema & Models

### A. Accounts Component

#### `User` (Extends `AbstractUser`)
*   **Table name:** `accounts_user`
*   **Fields:**
    *   `id` (UUIDField, Primary Key, default: `uuid.uuid4`)
    *   `email` (EmailField, Unique, Used as Username)
    *   `first_name` (CharField, max 30)
    *   `last_name` (CharField, max 30)
    *   `is_active` (BooleanField, default: `True`)
    *   `is_staff` (BooleanField, default: `False`)
    *   `date_joined` (DateTimeField, default: `timezone.now`)
    *   `last_login` (DateTimeField, null/blank)
*   **Properties/Methods:**
    *   `full_name` -> Returns `"First Last"`
    *   `get_initials()` -> Returns upper initials (e.g., `"JD"`)

#### `Profile`
*   **Table name:** `accounts_profile`
*   **Fields:**
    *   `user` (OneToOneField on `User`, related name: `profile`)
    *   `phone_number` (CharField, regex validated `+999999999` up to 15 digits, max length 17)
    *   `bio` (TextField, max 500, blank)
    *   `location` (CharField, max 100, blank)
    *   `birth_date` (DateField, null/blank)
    *   `avatar` (ImageField, uploads to Cloudinary storage via dynamic settings in production)
    *   `website` (URLField, blank)
    *   `timezone` (CharField, default: `'UTC'`)
    *   `notification_preferences` (JSONField, default: `dict`)
    *   `created_at` (DateTimeField, auto_now_add)
    *   `updated_at` (DateTimeField, auto_now)

#### `UserRole`
*   **Table name:** `accounts_user_role`
*   **Fields:**
    *   `user` (OneToOneField on `User`, related name: `role`)
    *   `role` (CharField, choices: `admin`, `manager`, `member`, `viewer`, default: `member`)
    *   `permissions` (JSONField, default: `list`)
    *   `assigned_by` (ForeignKey on `User`, null/blank, related name: `assigned_roles`)
    *   `assigned_at` (DateTimeField, auto_now_add)
    *   `updated_at` (DateTimeField, auto_now)

#### `PasswordResetToken`
*   **Table name:** `accounts_password_reset_token`
*   **Fields:**
    *   `id` (BigAutoField, Primary Key)
    *   `user` (ForeignKey on `User`, related name: `password_reset_tokens`)
    *   `token` (CharField, max 255, unique)
    *   `created_at` (DateTimeField, auto_now_add)
    *   `used` (BooleanField, default: `False`)
*   **Methods:**
    *   `is_expired()` -> Checks if current time exceeds token age + `PASSWORD_RESET_TIMEOUT` (default: 259,200 seconds / 3 days)

---

### B. Tasks Component

#### `Category`
*   **Table name:** `tasks_category`
*   **Fields:**
    *   `id` (UUIDField, Primary Key, default: `uuid.uuid4`)
    *   `name` (CharField, max 100)
    *   `description` (TextField, blank)
    *   `color` (CharField, Hex Code, default: `#3B82F6`)
    *   `icon` (CharField, max 50, blank)
    *   `user` (ForeignKey on `User`, related name: `categories`)
    *   `is_default` (BooleanField, default: `False`)
    *   `created_at` (DateTimeField, auto_now_add)
    *   `updated_at` (DateTimeField, auto_now)
*   **Constraints:**
    *   `unique_together` on `['name', 'user']`

#### `Task`
*   **Table name:** `tasks_task`
*   **Fields:**
    *   `id` (UUIDField, Primary Key, default: `uuid.uuid4`)
    *   `title` (CharField, max 200)
    *   `description` (TextField, blank)
    *   `status` (CharField choices: `pending`, `in_progress`, `completed`, `cancelled`, default: `pending`)
    *   `priority` (CharField choices: `low`, `medium`, `high`, `urgent`, default: `medium`)
    *   `category` (ForeignKey on `Category`, nullable, related name: `tasks`)
    *   `user` (ForeignKey on `User`, related name: `tasks`)
    *   `assigned_to` (ForeignKey on `User`, nullable, related name: `assigned_tasks`)
    *   `due_date` (DateTimeField, null/blank)
    *   `start_date` (DateTimeField, null/blank)
    *   `estimated_hours` (DecimalField, `max_digits=5`, `decimal_places=2`, null/blank)
    *   `actual_hours` (DecimalField, `max_digits=5`, `decimal_places=2`, null/blank)
    *   `completed_at` (DateTimeField, null/blank)
    *   `tags` (JSONField, default: `list`, blank)
    *   `is_recurring` (BooleanField, default: `False`)
    *   `recurrence_pattern` (JSONField, default: `dict`, blank)
    *   `parent_task` (ForeignKey on `Task`, nullable, related name: `subtasks`)
    *   `position` (PositiveIntegerField, default: `0`)
    *   `created_at` (DateTimeField, auto_now_add)
    *   `updated_at` (DateTimeField, auto_now)
*   **Properties/Methods:**
    *   `is_overdue` -> Returns True if due_date is passed and status is not completed.
    *   `is_due_today` -> Returns True if due_date is today.

#### `TaskComment`
*   **Table name:** `tasks_task_comment`
*   **Fields:**
    *   `id` (UUIDField, Primary Key, default: `uuid.uuid4`)
    *   `task` (ForeignKey on `Task`, related name: `comments`)
    *   `user` (ForeignKey on `User`, related name: `task_comments`)
    *   `content` (TextField)
    *   `is_internal` (BooleanField, default: `False`, viewable only by assignees)
    *   `created_at` (DateTimeField, auto_now_add)
    *   `updated_at` (DateTimeField, auto_now)

#### `TaskAttachment`
*   **Table name:** `tasks_task_attachment`
*   **Fields:**
    *   `id` (UUIDField, Primary Key, default: `uuid.uuid4`)
    *   `task` (ForeignKey on `Task`, related name: `attachments`)
    *   `user` (ForeignKey on `User`, related name: `uploaded_attachments`)
    *   `file` (FileField, uploads to MediaCloudinaryStorage or local storage)
    *   `file_name` (CharField, max 255)
    *   `file_size` (PositiveIntegerField)
    *   `file_type` (CharField, max 100)
    *   `uploaded_at` (DateTimeField, auto_now_add)

---

### C. Analytics Component

#### `DailyStats`
*   **Table name:** `analytics_daily_stats`
*   **Fields:**
    *   `id` (UUIDField, Primary Key, default: `uuid.uuid4`)
    *   `user` (ForeignKey on `User`, related name: `daily_stats`)
    *   `date` (DateField)
    *   `tasks_created` (PositiveIntegerField, default: 0)
    *   `tasks_completed` (PositiveIntegerField, default: 0)
    *   `tasks_overdue` (PositiveIntegerField, default: 0)
    *   `hours_worked` (DecimalField, max_digits=5, decimal_places=2, default: `0.00`)
    *   `productivity_score` (DecimalField, max_digits=5, decimal_places=2, default: `0.00`)
    *   `categories_data` (JSONField, default: `dict`)
    *   `created_at` (DateTimeField, auto_now_add)
    *   `updated_at` (DateTimeField, auto_now)
*   **Properties/Methods:**
    *   `completion_rate` -> Calculated completion percentage: `(tasks_completed / tasks_created) * 100`.

#### `WeeklyStats`
*   **Table name:** `analytics_weekly_stats`
*   **Fields:**
    *   `id` (UUIDField, Primary Key, default: `uuid.uuid4`)
    *   `user` (ForeignKey on `User`, related name: `weekly_stats`)
    *   `year` (PositiveIntegerField)
    *   `week_number` (PositiveIntegerField)
    *   `start_date` (DateField)
    *   `end_date` (DateField)
    *   `total_tasks_created` (PositiveIntegerField, default: 0)
    *   `total_tasks_completed` (PositiveIntegerField, default: 0)
    *   `total_tasks_overdue` (PositiveIntegerField, default: 0)
    *   `total_hours_worked` (DecimalField, max_digits=6, decimal_places=2, default: `0.00`)
    *   `average_productivity_score` (DecimalField, max_digits=5, decimal_places=2, default: `0.00`)
    *   `weekly_categories_data` (JSONField, default: `dict`)
    *   `daily_breakdown` (JSONField, default: `list`)
    *   `created_at` (DateTimeField, auto_now_add)
    *   `updated_at` (DateTimeField, auto_now)
*   **Properties/Methods:**
    *   `completion_rate` -> Calculated weekly completion percentage: `(total_tasks_completed / total_tasks_created) * 100`.

---

## 4. API Endpoint Catalog

All routes are versioned and prefixed with `/api/v1/`. All endpoints except registration, login, token refresh, Google auth URL, Google callback, and password reset requests/confirms require a JWT token in the `Authorization` header (`Bearer <access_token>`).

### A. Authentication & SSO (`/api/v1/auth/`)

| Method | Endpoint | Request Payload | Response Schema (Success) |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/register/` | `{ first_name, last_name, email, password, password_confirm }` | User info & JWT tokens: `{ user: {...}, tokens: { access, refresh }, message }` |
| `POST` | `/auth/login/` | `{ email, password }` | JWT Auth tokens: `{ user: {...}, access, refresh }` |
| `POST` | `/auth/logout/` | `{ refresh }` (refresh token string) | `{ "message": "Logout successful" }` |
| `POST` | `/auth/token/refresh/` | `{ refresh }` (refresh token string) | `{ "access": "..." }` |
| `POST` | `/auth/password/change/` | `{ old_password, new_password, new_password_confirm }` | `{ "message": "Password changed successfully" }` |
| `POST` | `/auth/password/reset/` | `{ email }` | `{ "message": "If an account exists with this email, a reset link will be sent." }` |
| `POST` | `/auth/password/reset/confirm/` | `{ token, new_password, new_password_confirm }` | `{ "message": "Password reset successful" }` |
| `GET` | `/auth/google/url/` | None | `{ "url": "https://accounts.google.com/o/oauth2/..." }` |
| `POST` | `/auth/google/callback/` | `{ code }` (Google code parameter) | JWT Auth tokens: `{ registered, is_new, access, refresh, user: {...}, message }` |

---

### B. User Details & Profiles (`/api/v1/users/`)

| Method | Endpoint | Request Payload | Response Schema (Success) |
| :--- | :--- | :--- | :--- |
| `GET` | `/users/me/` | None | `{ id, email, first_name, last_name, full_name, initials }` |
| `GET` | `/users/profile/` | None | `{ phone_number, bio, location, birth_date, avatar, website, timezone, notification_preferences }` |
| `PATCH` | `/users/profile/` | Form data: `{ phone_number, bio, location, avatar (File), website, timezone }` | Updated profile object |

---

### C. Category Management (`/api/v1/categories/`)

| Method | Endpoint | Request Payload | Response Schema (Success) |
| :--- | :--- | :--- | :--- |
| `GET` | `/categories/` | None | Paginated category list: `{ count, next, previous, results: [...] }` or flat list |
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
| `GET` | `/tasks/today/` | None (Query param filter helper) | List of tasks due today |
| `GET` | `/tasks/overdue/` | None (Query param filter helper) | List of pending overdue tasks |
| `GET` | `/tasks/completed/` | None (Query param filter helper) | List of tasks completed in past 7 days |
| `GET` | `/tasks/upcoming/` | None (Query param filter helper) | List of upcoming tasks next 7 days |
| `PATCH` | `/tasks/<id>/update_status/` | `{ status }` | Updated task object |
| `POST` | `/tasks/<id>/toggle_complete/` | None | Toggles between completed and pending |
| `POST` | `/tasks/bulk_action/` | `{ task_ids: [UUID, ...], action: 'complete'\|'delete'\|'change_priority'\|'change_status', value: '...' }` | `{ "message": "Bulk action applied to X tasks" }` |

---

### E. Task Comments & Attachments (`/api/v1/tasks/<id>/`)

| Method | Endpoint | Request Payload | Response Schema (Success) |
| :--- | :--- | :--- | :--- |
| `GET` | `/tasks/<id>/comments/` | None | List of task comments |
| `POST` | `/tasks/<id>/comments/` | `{ content, is_internal }` | Created comment object |
| `DELETE` | `/tasks/<id>/comments/<cid>/` | None | `204 No Content` |
| `GET` | `/tasks/<id>/attachments/` | None | List of task attachments |
| `POST` | `/tasks/<id>/attachments/` | Form data: `{ file }` | Created attachment object |
| `DELETE` | `/tasks/<id>/attachments/<aid>/` | None | `204 No Content` |

---

### F. Analytics & Reporting (`/api/v1/analytics/`)

*(Note: These routes are fully configured on the backend but are not currently hit by the frontend, which handles stats locally.)*

| Method | Endpoint | Request Payload | Response Schema (Success) |
| :--- | :--- | :--- | :--- |
| `GET` | `/analytics/overview/` | None | `{ total_tasks, completed_tasks, pending_tasks, in_progress_tasks, cancelled_tasks, overdue_tasks, due_today, tasks_this_week, completed_this_week, completion_rate, productivity_score }` |
| `GET` | `/analytics/daily/` | Query params: `days` (default 30) | List of daily stats objects |
| `GET` | `/analytics/weekly/` | Query params: `weeks` (default 12) | List of weekly stats objects |
| `GET` | `/analytics/trends/` | Query params: `days` (default 14) | Chart-friendly trends: `[{ date, tasks_created, tasks_completed, completion_rate, productivity_score }]` |
| `GET` | `/analytics/categories/` | None | Categorized counts: `[{ category_id, category_name, category_color, total_tasks, completed_tasks, pending_tasks, overdue_tasks, completion_rate }]` |

---

## 5. Security & Permissions Architecture (`core/permissions.py`)

Permissions enforce security policies across views. Custom permission classes are:

1.  **`IsOwner`:** Matches the `user` or `owner` foreign key attribute of an object with `request.user`.
2.  **`IsOwnerOrReadOnly`:** Allows access to SAFE_METHODS (`GET`, `HEAD`, `OPTIONS`) to all authenticated users, restricting writes to the object owner.
3.  **`IsAdminUser`:** Restricts access to users with `is_superuser=True` or `role='admin'`.
4.  **`IsManagerOrAdmin`:** Restricts access to managers or admin users.
5.  **`IsProfileOwnerOrReadOnly`:** Restricts profile writes to the owner.
6.  **`IsTaskOwnerOrAssigned`:** Restricts task editing to the creator, but allows read access and status patching (`update_status`) to the assigned user.
7.  **`CanCreateTask`:** Enforces that users with a viewer role cannot create tasks.
8.  **`CanManageUsers`:** Restricts user creation/management to admins.
9.  **`CanViewAnalytics`:** Grants user access to run analytics aggregations (checks object ownership).

---

## 6. Background Asynchronous Actions (Celery)

Celery processes long-running workflows asynchronously inside task queries:

*   **`send_email_task`**: Generic asynchronous task for email delivery.
*   **`send_welcome_email`**: Dispatched after user registration. Sends an HTML branded onboarding email.
*   **`send_password_reset_email`**: Triggered on request reset. Generates a path link with the query string token parameter pointing to the frontend.
*   **`send_password_changed_email`**: Triggered after password change view updates.

---

## 7. Frontend-Backend Compatibility & Alignment Map

The following compatibility table documents key alignment and gaps between the frontend (`acta-frontend`) and the backend (`Acta_backend`):

### 📋 Synchronization Map

| Area / Feature | Backend Implementation (`Acta_backend`) | Frontend Expectation (`acta-frontend`) | Status & Mapping Strategy |
| :--- | :--- | :--- | :--- |
| **Task Status Enums** | Uses `"pending"`, `"in_progress"`, `"completed"`, `"cancelled"` | Uses `"todo"`, `"in_progress"`, `"completed"` | **Mapped**: Mapped at the api layer `src/api/tasks.ts` intercepting server payloads: `"todo" <=> "pending"`. |
| **Date Fields** | Expects `due_date` and `created_at` (snake_case) | Maps `due_date` (`dueDate` fallback) and `created_at` (`createdAt` fallback) | **Aligned**: Compatible. Server outputs standard ISO 8601 strings. |
| **Category List** | Returns paginated format `{ results: [...] }` by default | Pulls list from `data.results \|\| data` | **Aligned**: Compatible. Client extracts results array transparently. |
| **Task Lists** | Returns paginated format `{ results: [...] }` | Pulls list from `data.results \|\| data` | **Aligned**: Compatible. Client extracts results array transparently. |
| **Analytics metrics**| Configured under `/api/v1/analytics/...` | Computed **entirely client-side** using raw `/tasks/` responses | **Bypassed**: The frontend ignores the backend analytics endpoints to perform real-time client-side calculation of streaks, completion rates, and daily progress. |
| **Task Quick Actions**| Exposes endpoints `/tasks/today/`, `/tasks/overdue/`, `/tasks/completed/`, `/tasks/upcoming/`, `/tasks/bulk_action/`, `/tasks/<id>/toggle_complete/` | None. Standard queries are filtered client-side | **Bypassed**: Extra endpoints remain in backend API catalog for future dashboard features, but client avoids using them. |
| **Social Login** | Supports Google OAuth2 (`/auth/google/url/` and `/auth/google/callback/`) | Aligned. Callback fetches tokens and updates localStorage | **Aligned**: Fully integrated. Facebook OAuth flow has been removed from both codebases. |
| **Contact Form** | None (No server-side contact API) | Uses `EmailJS` third-party integration directly | **Bypassed**: Contact inquiries bypass the backend entirely to save on transactional email volumes. |
