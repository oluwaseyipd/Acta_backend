"""
Comprehensive tests for task views and functionality.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from tasks.models import Task, Category, TaskComment, TaskAttachment


@pytest.mark.django_db
class TestTaskViewSet:
    """Tests for TaskViewSet."""

    def test_list_tasks(self, authenticated_client, task):
        """Test listing tasks for authenticated user."""
        url = reverse('task-list')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == task.title

    def test_create_task(self, authenticated_client, category):
        """Test creating a new task."""
        url = reverse('task-list')
        data = {
            'title': 'New Task',
            'description': 'Task description',
            'priority': 'high',
            'status': 'pending',
            'category': category.id
        }
        response = authenticated_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Task.objects.filter(title='New Task').exists()

        created_task = Task.objects.get(title='New Task')
        assert created_task.priority == Task.Priority.HIGH
        assert created_task.category == category

    def test_retrieve_task(self, authenticated_client, task):
        """Test retrieving a specific task."""
        url = reverse('task-detail', kwargs={'pk': task.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == task.title
        assert response.data['description'] == task.description

    def test_update_task(self, authenticated_client, task):
        """Test updating a task."""
        url = reverse('task-detail', kwargs={'pk': task.id})
        data = {'title': 'Updated Task', 'priority': 'urgent'}
        response = authenticated_client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.title == 'Updated Task'
        assert task.priority == Task.Priority.URGENT

    def test_delete_task(self, authenticated_client, task):
        """Test deleting a task."""
        url = reverse('task-detail', kwargs={'pk': task.id})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Task.objects.filter(id=task.id).exists()

    def test_toggle_complete(self, authenticated_client, task):
        """Test toggling task completion status."""
        url = reverse('task-toggle-complete', kwargs={'pk': task.id})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.status == Task.Status.COMPLETED
        assert task.completed_at is not None

        # Toggle back to incomplete
        response = authenticated_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.status == Task.Status.PENDING
        assert task.completed_at is None

    def test_update_status(self, authenticated_client, task):
        """Test updating task status."""
        url = reverse('task-update-status', kwargs={'pk': task.id})
        data = {'status': 'in_progress'}
        response = authenticated_client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.status == Task.Status.IN_PROGRESS

    def test_today_tasks(self, authenticated_client, user):
        """Test getting tasks due today."""
        today = timezone.now().date()
        task_today = Task.objects.create(
            user=user,
            title='Today Task',
            due_date=timezone.now().replace(hour=12, minute=0),
            priority=Task.Priority.HIGH,
            status=Task.Status.PENDING
        )

        url = reverse('task-today')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        task_titles = [task['title'] for task in response.data]
        assert 'Today Task' in task_titles

    def test_overdue_tasks(self, authenticated_client, overdue_task):
        """Test getting overdue tasks."""
        url = reverse('task-overdue')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['title'] == overdue_task.title

    def test_completed_tasks(self, authenticated_client, completed_task):
        """Test getting recently completed tasks."""
        url = reverse('task-completed')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['title'] == completed_task.title

    def test_upcoming_tasks(self, authenticated_client, user):
        """Test getting upcoming tasks."""
        # Create task for next week
        upcoming_task = Task.objects.create(
            user=user,
            title='Upcoming Task',
            due_date=timezone.now() + timedelta(days=3),
            priority=Task.Priority.MEDIUM,
            status=Task.Status.PENDING
        )

        url = reverse('task-upcoming')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        task_titles = [task['title'] for task in response.data]
        assert 'Upcoming Task' in task_titles

    def test_bulk_action_complete(self, authenticated_client, multiple_tasks):
        """Test bulk completion of tasks."""
        task_ids = [str(task.id) for task in multiple_tasks[:3]]

        url = reverse('task-bulk-action')
        data = {
            'task_ids': task_ids,
            'action': 'complete'
        }
        response = authenticated_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK

        # Check that tasks are completed
        for task_id in task_ids:
            task = Task.objects.get(id=task_id)
            assert task.status == Task.Status.COMPLETED

    def test_bulk_action_delete(self, authenticated_client, multiple_tasks):
        """Test bulk deletion of tasks."""
        task_ids = [str(task.id) for task in multiple_tasks[:2]]
        initial_count = Task.objects.count()

        url = reverse('task-bulk-action')
        data = {
            'task_ids': task_ids,
            'action': 'delete'
        }
        response = authenticated_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert Task.objects.count() == initial_count - 2

    def test_task_filtering(self, authenticated_client, multiple_tasks):
        """Test task filtering functionality."""
        url = reverse('task-list')

        # Filter by status
        response = authenticated_client.get(url, {'status': 'pending'})
        assert response.status_code == status.HTTP_200_OK

        # Filter by priority
        response = authenticated_client.get(url, {'priority': 'high'})
        assert response.status_code == status.HTTP_200_OK

        # Filter by overdue
        response = authenticated_client.get(url, {'is_overdue': 'true'})
        assert response.status_code == status.HTTP_200_OK

    def test_task_search(self, authenticated_client, task):
        """Test task search functionality."""
        url = reverse('task-list')
        response = authenticated_client.get(url, {'search': 'Test'})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1

    def test_task_ordering(self, authenticated_client, multiple_tasks):
        """Test task ordering functionality."""
        url = reverse('task-list')

        # Order by due_date
        response = authenticated_client.get(url, {'ordering': 'due_date'})
        assert response.status_code == status.HTTP_200_OK

        # Order by priority descending
        response = authenticated_client.get(url, {'ordering': '-priority'})
        assert response.status_code == status.HTTP_200_OK

    def test_unauthorized_access(self, api_client):
        """Test that unauthenticated requests are rejected."""
        url = reverse('task-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_isolation(self, authenticated_client, api_client, multiple_users):
        """Test that users can only see their own tasks."""
        # Create tasks for different users
        user1, user2 = multiple_users[0], multiple_users[1]

        Task.objects.create(
            user=user1,
            title='User 1 Task',
            priority=Task.Priority.HIGH,
            status=Task.Status.PENDING
        )

        Task.objects.create(
            user=user2,
            title='User 2 Task',
            priority=Task.Priority.HIGH,
            status=Task.Status.PENDING
        )

        # Authenticate as user1
        api_client.force_authenticate(user=user1)
        url = reverse('task-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        task_titles = [task['title'] for task in response.data['results']]
        assert 'User 1 Task' in task_titles
        assert 'User 2 Task' not in task_titles


@pytest.mark.django_db
class TestCategoryViewSet:
    """Tests for CategoryViewSet."""

    def test_list_categories(self, authenticated_client, category):
        """Test listing categories."""
        url = reverse('category-list')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == category.name

    def test_create_category(self, authenticated_client):
        """Test creating a new category."""
        url = reverse('category-list')
        data = {
            'name': 'New Category',
            'color': '#123456',
            'icon': 'new-icon',
            'description': 'New category description'
        }
        response = authenticated_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Category.objects.filter(name='New Category').exists()

    def test_update_category(self, authenticated_client, category):
        """Test updating a category."""
        url = reverse('category-detail', kwargs={'pk': category.id})
        data = {'name': 'Updated Category', 'color': '#654321'}
        response = authenticated_client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        category.refresh_from_db()
        assert category.name == 'Updated Category'
        assert category.color == '#654321'

    def test_delete_category(self, authenticated_client, category):
        """Test deleting a category."""
        url = reverse('category-detail', kwargs={'pk': category.id})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Category.objects.filter(id=category.id).exists()

    def test_category_user_isolation(self, api_client, multiple_users):
        """Test that users can only see their own categories."""
        user1, user2 = multiple_users[0], multiple_users[1]

        Category.objects.create(user=user1, name='User 1 Category', color='#111111')
        Category.objects.create(user=user2, name='User 2 Category', color='#222222')

        api_client.force_authenticate(user=user1)
        url = reverse('category-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        category_names = [cat['name'] for cat in response.data['results']]
        assert 'User 1 Category' in category_names
        assert 'User 2 Category' not in category_names


@pytest.mark.django_db
class TestTaskCommentViewSet:
    """Tests for TaskCommentViewSet."""

    def test_list_comments(self, authenticated_client, task, task_comment):
        """Test listing task comments."""
        url = reverse('task-comments-list', kwargs={'task_pk': task.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['content'] == task_comment.content

    def test_create_comment(self, authenticated_client, task):
        """Test creating a task comment."""
        url = reverse('task-comments-list', kwargs={'task_pk': task.id})
        data = {'content': 'New comment content'}
        response = authenticated_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert TaskComment.objects.filter(content='New comment content').exists()

    def test_update_comment(self, authenticated_client, task, task_comment):
        """Test updating a task comment."""
        url = reverse('task-comments-detail', kwargs={
            'task_pk': task.id,
            'pk': task_comment.id
        })
        data = {'content': 'Updated comment content'}
        response = authenticated_client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        task_comment.refresh_from_db()
        assert task_comment.content == 'Updated comment content'

    def test_delete_comment(self, authenticated_client, task, task_comment):
        """Test deleting a task comment."""
        url = reverse('task-comments-detail', kwargs={
            'task_pk': task.id,
            'pk': task_comment.id
        })
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not TaskComment.objects.filter(id=task_comment.id).exists()


@pytest.mark.django_db
class TestTaskModel:
    """Tests for Task model."""

    def test_task_creation(self, user, category):
        """Test task creation with all fields."""
        task = Task.objects.create(
            user=user,
            title='Test Task',
            description='Test description',
            priority=Task.Priority.HIGH,
            status=Task.Status.PENDING,
            category=category,
            due_date=timezone.now() + timedelta(days=1),
            estimated_hours=8.5
        )

        assert task.user == user
        assert task.title == 'Test Task'
        assert task.priority == Task.Priority.HIGH
        assert task.status == Task.Status.PENDING
        assert task.category == category
        assert task.estimated_hours == 8.5

    def test_task_str(self, task):
        """Test task string representation."""
        assert str(task) == task.title

    def test_is_overdue(self, user, category):
        """Test is_overdue property."""
        # Create overdue task
        overdue_task = Task.objects.create(
            user=user,
            title='Overdue Task',
            due_date=timezone.now() - timedelta(days=1),
            status=Task.Status.PENDING
        )

        # Create future task
        future_task = Task.objects.create(
            user=user,
            title='Future Task',
            due_date=timezone.now() + timedelta(days=1),
            status=Task.Status.PENDING
        )

        # Create completed overdue task
        completed_task = Task.objects.create(
            user=user,
            title='Completed Task',
            due_date=timezone.now() - timedelta(days=1),
            status=Task.Status.COMPLETED
        )

        assert overdue_task.is_overdue is True
        assert future_task.is_overdue is False
        assert completed_task.is_overdue is False

    def test_is_due_today(self, user):
        """Test is_due_today property."""
        today_task = Task.objects.create(
            user=user,
            title='Today Task',
            due_date=timezone.now(),
            status=Task.Status.PENDING
        )

        tomorrow_task = Task.objects.create(
            user=user,
            title='Tomorrow Task',
            due_date=timezone.now() + timedelta(days=1),
            status=Task.Status.PENDING
        )

        assert today_task.is_due_today is True
        assert tomorrow_task.is_due_today is False

    def test_task_completion_signal(self, user):
        """Test that completion timestamp is set automatically."""
        task = Task.objects.create(
            user=user,
            title='Test Task',
            status=Task.Status.PENDING
        )

        assert task.completed_at is None

        # Complete the task
        task.status = Task.Status.COMPLETED
        task.save()

        task.refresh_from_db()
        assert task.completed_at is not None
        assert task.status == Task.Status.COMPLETED
