"""
Pytest configuration and fixtures for Acta backend testing.
"""
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

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
def admin_user(db):
    """Create and return an admin user."""
    return User.objects.create_superuser(
        email='admin@example.com',
        password='adminpass123',
        first_name='Admin',
        last_name='User'
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """Return an authenticated API client."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """Return an authenticated admin API client."""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def category(user):
    """Create and return a test category."""
    from tasks.models import Category
    return Category.objects.create(
        user=user,
        name='Test Category',
        color='#FF5733',
        icon='test-icon',
        description='Test category description'
    )


@pytest.fixture
def task(user, category):
    """Create and return a test task."""
    from tasks.models import Task
    return Task.objects.create(
        user=user,
        title='Test Task',
        description='Test description',
        priority=Task.Priority.MEDIUM,
        status=Task.Status.PENDING,
        category=category,
        due_date=timezone.now() + timedelta(days=1)
    )


@pytest.fixture
def completed_task(user, category):
    """Create and return a completed test task."""
    from tasks.models import Task
    return Task.objects.create(
        user=user,
        title='Completed Task',
        description='Completed test description',
        priority=Task.Priority.HIGH,
        status=Task.Status.COMPLETED,
        category=category,
        completed_at=timezone.now()
    )


@pytest.fixture
def overdue_task(user, category):
    """Create and return an overdue test task."""
    from tasks.models import Task
    return Task.objects.create(
        user=user,
        title='Overdue Task',
        description='Overdue test description',
        priority=Task.Priority.URGENT,
        status=Task.Status.IN_PROGRESS,
        category=category,
        due_date=timezone.now() - timedelta(days=1)
    )


@pytest.fixture
def task_comment(task, user):
    """Create and return a test task comment."""
    from tasks.models import TaskComment
    return TaskComment.objects.create(
        task=task,
        user=user,
        content='Test comment content'
    )


@pytest.fixture
def daily_stats(user):
    """Create and return test daily stats."""
    from analytics.models import DailyStats
    from decimal import Decimal
    return DailyStats.objects.create(
        user=user,
        date=timezone.now().date(),
        tasks_created=5,
        tasks_completed=3,
        tasks_overdue=1,
        hours_worked=Decimal('8.50'),
        productivity_score=Decimal('75.00'),
        categories_data={
            'test_category': {
                'name': 'Test Category',
                'tasks_created': 5,
                'tasks_completed': 3
            }
        }
    )


@pytest.fixture
def multiple_users(db):
    """Create and return multiple test users."""
    users = []
    for i in range(3):
        user = User.objects.create_user(
            email=f'user{i}@example.com',
            password='testpass123',
            first_name=f'User{i}',
            last_name='Test'
        )
        users.append(user)
    return users


@pytest.fixture
def multiple_tasks(user, category):
    """Create and return multiple test tasks."""
    from tasks.models import Task
    tasks = []
    priorities = [Task.Priority.LOW, Task.Priority.MEDIUM, Task.Priority.HIGH, Task.Priority.URGENT]
    statuses = [Task.Status.PENDING, Task.Status.IN_PROGRESS, Task.Status.COMPLETED]

    for i in range(10):
        task = Task.objects.create(
            user=user,
            title=f'Test Task {i+1}',
            description=f'Test description {i+1}',
            priority=priorities[i % len(priorities)],
            status=statuses[i % len(statuses)],
            category=category,
            due_date=timezone.now() + timedelta(days=i+1)
        )
        tasks.append(task)

    return tasks


@pytest.fixture
def jwt_tokens(user):
    """Create and return JWT tokens for a user."""
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }


@pytest.fixture
def profile(user):
    """Get or create user profile."""
    from accounts.models import Profile
    profile, created = Profile.objects.get_or_create(
        user=user,
        defaults={
            'bio': 'Test bio',
            'timezone': 'UTC',
            'notification_preferences': {'email': True, 'push': False}
        }
    )
    return profile
