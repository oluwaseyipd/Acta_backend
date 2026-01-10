"""
Comprehensive tests for analytics views and functionality.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from analytics.models import DailyStats, WeeklyStats


@pytest.mark.django_db
class TestOverviewStatsView:
    """Tests for OverviewStatsView."""

    def test_get_overview_stats(self, authenticated_client, user, multiple_tasks):
        """Test getting overview statistics."""
        url = reverse('overview_stats')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        # Check required fields
        required_fields = [
            'total_tasks', 'completed_tasks', 'pending_tasks',
            'in_progress_tasks', 'cancelled_tasks', 'overdue_tasks',
            'due_today', 'completion_rate', 'tasks_this_week',
            'completed_this_week', 'productivity_score'
        ]

        for field in required_fields:
            assert field in response.data

        # Check data types
        assert isinstance(response.data['total_tasks'], int)
        assert isinstance(response.data['completion_rate'], float)
        assert isinstance(response.data['productivity_score'], float)

    def test_overview_stats_empty_data(self, authenticated_client, user):
        """Test overview stats with no tasks."""
        url = reverse('overview_stats')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_tasks'] == 0
        assert response.data['completion_rate'] == 0.0
        assert response.data['productivity_score'] == 0.0

    def test_overview_stats_unauthenticated(self, api_client):
        """Test overview stats without authentication."""
        url = reverse('overview_stats')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_overview_stats_completion_rate_calculation(self, authenticated_client, user):
        """Test completion rate calculation in overview stats."""
        from tasks.models import Task, Category

        # Create category
        category = Category.objects.create(user=user, name='Test Category', color='#FF5733')

        # Create tasks with different statuses
        Task.objects.create(user=user, title='Task 1', status=Task.Status.COMPLETED, category=category)
        Task.objects.create(user=user, title='Task 2', status=Task.Status.COMPLETED, category=category)
        Task.objects.create(user=user, title='Task 3', status=Task.Status.PENDING, category=category)
        Task.objects.create(user=user, title='Task 4', status=Task.Status.IN_PROGRESS, category=category)

        url = reverse('overview_stats')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_tasks'] == 4
        assert response.data['completed_tasks'] == 2
        assert response.data['completion_rate'] == 50.0


@pytest.mark.django_db
class TestDailyStatsView:
    """Tests for DailyStatsView."""

    def test_list_daily_stats(self, authenticated_client, daily_stats):
        """Test listing daily statistics."""
        url = reverse('daily_stats')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['tasks_created'] == daily_stats.tasks_created

    def test_daily_stats_filtering_by_days(self, authenticated_client, user):
        """Test filtering daily stats by number of days."""
        # Create stats for different dates
        today = timezone.now().date()
        for i in range(5):
            date = today - timedelta(days=i)
            DailyStats.objects.create(
                user=user,
                date=date,
                tasks_created=i+1,
                tasks_completed=i,
                productivity_score=Decimal('50.0')
            )

        url = reverse('daily_stats')
        response = authenticated_client.get(url, {'days': 3})

        assert response.status_code == status.HTTP_200_OK
        # Should return stats for last 3 days plus today (4 total)
        assert len(response.data['results']) == 4

    def test_daily_stats_ordering(self, authenticated_client, user):
        """Test that daily stats are ordered by date."""
        today = timezone.now().date()
        for i in range(3):
            date = today - timedelta(days=i)
            DailyStats.objects.create(
                user=user,
                date=date,
                tasks_created=i+1,
                tasks_completed=i,
                productivity_score=Decimal('50.0')
            )

        url = reverse('daily_stats')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        # Check that results are ordered by date (ascending)
        dates = [item['date'] for item in response.data['results']]
        assert dates == sorted(dates)

    def test_daily_stats_user_isolation(self, api_client, multiple_users):
        """Test that users only see their own daily stats."""
        user1, user2 = multiple_users[0], multiple_users[1]
        today = timezone.now().date()

        # Create stats for both users
        DailyStats.objects.create(
            user=user1,
            date=today,
            tasks_created=5,
            tasks_completed=3,
            productivity_score=Decimal('60.0')
        )
        DailyStats.objects.create(
            user=user2,
            date=today,
            tasks_created=10,
            tasks_completed=8,
            productivity_score=Decimal('80.0')
        )

        # Authenticate as user1
        api_client.force_authenticate(user=user1)
        url = reverse('daily_stats')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['tasks_created'] == 5


@pytest.mark.django_db
class TestWeeklyStatsView:
    """Tests for WeeklyStatsView."""

    def test_list_weekly_stats(self, authenticated_client, user):
        """Test listing weekly statistics."""
        # Create weekly stats
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())

        WeeklyStats.objects.create(
            user=user,
            year=today.year,
            week_number=today.isocalendar()[1],
            start_date=week_start,
            end_date=week_start + timedelta(days=6),
            total_tasks_created=20,
            total_tasks_completed=15,
            average_productivity_score=Decimal('75.0')
        )

        url = reverse('weekly_stats')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['total_tasks_created'] == 20

    def test_weekly_stats_filtering_by_weeks(self, authenticated_client, user):
        """Test filtering weekly stats by number of weeks."""
        today = timezone.now().date()

        # Create stats for multiple weeks
        for i in range(4):
            week_start = today - timedelta(weeks=i, days=today.weekday())
            week_end = week_start + timedelta(days=6)
            year, week_num, _ = (week_start + timedelta(days=3)).isocalendar()

            WeeklyStats.objects.create(
                user=user,
                year=year,
                week_number=week_num,
                start_date=week_start,
                end_date=week_end,
                total_tasks_created=(i+1) * 5,
                total_tasks_completed=(i+1) * 3,
                average_productivity_score=Decimal('60.0')
            )

        url = reverse('weekly_stats')
        response = authenticated_client.get(url, {'weeks': 2})

        assert response.status_code == status.HTTP_200_OK
        # Should return stats for last 2 weeks
        assert len(response.data['results']) == 2


@pytest.mark.django_db
class TestProductivityTrendView:
    """Tests for ProductivityTrendView."""

    def test_get_productivity_trends(self, authenticated_client, user):
        """Test getting productivity trends."""
        from tasks.models import Task, Category

        # Create category
        category = Category.objects.create(user=user, name='Test Category', color='#FF5733')

        # Create tasks for trend calculation
        today = timezone.now()
        for i in range(3):
            date = today - timedelta(days=i)
            Task.objects.create(
                user=user,
                title=f'Task {i}',
                category=category,
                created_at=date,
                status=Task.Status.COMPLETED if i < 2 else Task.Status.PENDING,
                completed_at=date if i < 2 else None
            )

        url = reverse('productivity_trends')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) == 14  # Default 14 days

        # Check data structure
        if response.data:
            trend_item = response.data[0]
            required_fields = ['date', 'tasks_created', 'tasks_completed',
                             'completion_rate', 'productivity_score']
            for field in required_fields:
                assert field in trend_item

    def test_productivity_trends_custom_days(self, authenticated_client, user):
        """Test productivity trends with custom day range."""
        url = reverse('productivity_trends')
        response = authenticated_client.get(url, {'days': 7})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 7

    def test_productivity_trends_calculation(self, authenticated_client, user):
        """Test productivity trends completion rate calculation."""
        from tasks.models import Task, Category

        category = Category.objects.create(user=user, name='Test Category', color='#FF5733')
        today = timezone.now()

        # Create 2 tasks created today, 1 completed
        Task.objects.create(user=user, title='Task 1', category=category,
                          created_at=today, status=Task.Status.COMPLETED, completed_at=today)
        Task.objects.create(user=user, title='Task 2', category=category,
                          created_at=today, status=Task.Status.PENDING)

        url = reverse('productivity_trends')
        response = authenticated_client.get(url, {'days': 1})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

        trend_data = response.data[0]
        assert trend_data['tasks_created'] == 2
        assert trend_data['tasks_completed'] == 1
        assert trend_data['completion_rate'] == 50.0


@pytest.mark.django_db
class TestCategoryStatsView:
    """Tests for CategoryStatsView."""

    def test_get_category_stats(self, authenticated_client, user):
        """Test getting category statistics."""
        from tasks.models import Task, Category

        # Create categories
        category1 = Category.objects.create(user=user, name='Work', color='#FF5733')
        category2 = Category.objects.create(user=user, name='Personal', color='#33FF57')

        # Create tasks in categories
        Task.objects.create(user=user, title='Work Task 1', category=category1,
                          status=Task.Status.COMPLETED)
        Task.objects.create(user=user, title='Work Task 2', category=category1,
                          status=Task.Status.PENDING)
        Task.objects.create(user=user, title='Personal Task 1', category=category2,
                          status=Task.Status.COMPLETED)

        url = reverse('category_stats')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

        # Find work category stats
        work_stats = next((cat for cat in response.data if cat['category_name'] == 'Work'), None)
        assert work_stats is not None
        assert work_stats['total_tasks'] == 2
        assert work_stats['completed_tasks'] == 1
        assert work_stats['completion_rate'] == 50.0

    def test_category_stats_empty_categories(self, authenticated_client, user):
        """Test category stats with empty categories."""
        from tasks.models import Category

        # Create category with no tasks
        Category.objects.create(user=user, name='Empty Category', color='#FF5733')

        url = reverse('category_stats')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

        category_stats = response.data[0]
        assert category_stats['total_tasks'] == 0
        assert category_stats['completed_tasks'] == 0
        assert category_stats['completion_rate'] == 0.0

    def test_category_stats_user_isolation(self, api_client, multiple_users):
        """Test that users only see their own category stats."""
        from tasks.models import Task, Category

        user1, user2 = multiple_users[0], multiple_users[1]

        # Create categories and tasks for both users
        cat1 = Category.objects.create(user=user1, name='User1 Category', color='#FF5733')
        cat2 = Category.objects.create(user=user2, name='User2 Category', color='#33FF57')

        Task.objects.create(user=user1, title='User1 Task', category=cat1)
        Task.objects.create(user=user2, title='User2 Task', category=cat2)

        # Authenticate as user1
        api_client.force_authenticate(user=user1)
        url = reverse('category_stats')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['category_name'] == 'User1 Category'


@pytest.mark.django_db
class TestDailyStatsModel:
    """Tests for DailyStats model."""

    def test_daily_stats_creation(self, user):
        """Test daily stats creation."""
        today = timezone.now().date()
        stats = DailyStats.objects.create(
            user=user,
            date=today,
            tasks_created=10,
            tasks_completed=8,
            tasks_overdue=1,
            hours_worked=Decimal('7.5'),
            productivity_score=Decimal('85.0'),
            categories_data={'work': {'tasks_created': 5, 'tasks_completed': 4}}
        )

        assert stats.user == user
        assert stats.date == today
        assert stats.tasks_created == 10
        assert stats.tasks_completed == 8
        assert stats.hours_worked == Decimal('7.5')
        assert stats.productivity_score == Decimal('85.0')

    def test_daily_stats_completion_rate_property(self, user):
        """Test completion rate property calculation."""
        today = timezone.now().date()
        stats = DailyStats.objects.create(
            user=user,
            date=today,
            tasks_created=10,
            tasks_completed=6,
            productivity_score=Decimal('60.0')
        )

        assert stats.completion_rate == Decimal('60.00')

    def test_daily_stats_completion_rate_zero_tasks(self, user):
        """Test completion rate with zero tasks created."""
        today = timezone.now().date()
        stats = DailyStats.objects.create(
            user=user,
            date=today,
            tasks_created=0,
            tasks_completed=0,
            productivity_score=Decimal('0.0')
        )

        assert stats.completion_rate == Decimal('0.00')

    def test_daily_stats_str(self, user):
        """Test daily stats string representation."""
        today = timezone.now().date()
        stats = DailyStats.objects.create(
            user=user,
            date=today,
            tasks_created=5,
            tasks_completed=3,
            productivity_score=Decimal('60.0')
        )

        expected_str = f"{user.email} - {today}"
        assert str(stats) == expected_str

    def test_daily_stats_unique_constraint(self, user):
        """Test that user-date combination is unique."""
        today = timezone.now().date()

        DailyStats.objects.create(
            user=user,
            date=today,
            tasks_created=5,
            tasks_completed=3,
            productivity_score=Decimal('60.0')
        )

        # Creating another stats for same user and date should raise error
        with pytest.raises(Exception):  # IntegrityError
            DailyStats.objects.create(
                user=user,
                date=today,
                tasks_created=3,
                tasks_completed=2,
                productivity_score=Decimal('66.0')
            )


@pytest.mark.django_db
class TestWeeklyStatsModel:
    """Tests for WeeklyStats model."""

    def test_weekly_stats_creation(self, user):
        """Test weekly stats creation."""
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        year, week_number, _ = today.isocalendar()

        stats = WeeklyStats.objects.create(
            user=user,
            year=year,
            week_number=week_number,
            start_date=week_start,
            end_date=week_end,
            total_tasks_created=50,
            total_tasks_completed=40,
            total_hours_worked=Decimal('35.0'),
            average_productivity_score=Decimal('80.0'),
            weekly_categories_data={'work': {'tasks_created': 25, 'tasks_completed': 20}},
            daily_breakdown=[{'date': '2024-01-01', 'tasks_created': 5, 'tasks_completed': 4}]
        )

        assert stats.user == user
        assert stats.year == year
        assert stats.week_number == week_number
        assert stats.total_tasks_created == 50
        assert stats.total_tasks_completed == 40
        assert stats.total_hours_worked == Decimal('35.0')
        assert stats.average_productivity_score == Decimal('80.0')

    def test_weekly_stats_completion_rate_property(self, user):
        """Test weekly completion rate property."""
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        year, week_number, _ = today.isocalendar()

        stats = WeeklyStats.objects.create(
            user=user,
            year=year,
            week_number=week_number,
            start_date=week_start,
            end_date=week_end,
            total_tasks_created=20,
            total_tasks_completed=15,
            average_productivity_score=Decimal('75.0')
        )

        assert stats.completion_rate == Decimal('75.00')

    def test_weekly_stats_str(self, user):
        """Test weekly stats string representation."""
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        year, week_number, _ = today.isocalendar()

        stats = WeeklyStats.objects.create(
            user=user,
            year=year,
            week_number=week_number,
            start_date=week_start,
            end_date=week_end,
            total_tasks_created=20,
            total_tasks_completed=15,
            average_productivity_score=Decimal('75.0')
        )

        expected_str = f"{user.email} - Week {week_number}, {year}"
        assert str(stats) == expected_str

    def test_weekly_stats_unique_constraint(self, user):
        """Test that user-year-week combination is unique."""
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        year, week_number, _ = today.isocalendar()

        WeeklyStats.objects.create(
            user=user,
            year=year,
            week_number=week_number,
            start_date=week_start,
            end_date=week_end,
            total_tasks_created=20,
            total_tasks_completed=15,
            average_productivity_score=Decimal('75.0')
        )

        # Creating another stats for same user, year, and week should raise error
        with pytest.raises(Exception):  # IntegrityError
            WeeklyStats.objects.create(
                user=user,
                year=year,
                week_number=week_number,
                start_date=week_start,
                end_date=week_end,
                total_tasks_created=25,
                total_tasks_completed=20,
                average_productivity_score=Decimal('80.0')
            )


@pytest.mark.django_db
class TestAnalyticsPermissions:
    """Tests for analytics permissions."""

    def test_analytics_require_authentication(self, api_client):
        """Test that all analytics endpoints require authentication."""
        endpoints = [
            'overview_stats',
            'daily_stats',
            'weekly_stats',
            'productivity_trends',
            'category_stats'
        ]

        for endpoint in endpoints:
            url = reverse(endpoint)
            response = api_client.get(url)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_analytics_data_isolation(self, api_client, user, daily_stats):
        """Test that analytics data is properly isolated between users."""
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Create a second user
        user2 = User.objects.create_user(
            email='user2@example.com',
            password='testpass123',
            first_name='User2',
            last_name='Test'
        )
        user1 = user

        # Create daily stats for user2
        today = timezone.now().date()
        DailyStats.objects.create(
            user=user2,
            date=today,
            tasks_created=100,
            tasks_completed=50,
            productivity_score=Decimal('50.0')
        )

        # Authenticate as user1 (daily_stats fixture belongs to user1)
        api_client.force_authenticate(user=user1)

        url = reverse('daily_stats')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Should only see user1's stats
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['tasks_created'] == daily_stats.tasks_created
        # Should not see user2's stats with 100 tasks_created
        assert not any(item['tasks_created'] == 100 for item in response.data['results'])
