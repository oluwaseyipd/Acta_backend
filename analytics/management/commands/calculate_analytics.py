"""
Management command to calculate daily/weekly analytics.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Count, Q
from decimal import Decimal
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
        parser.add_argument(
            '--user',
            type=str,
            help='Calculate for specific user email',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Calculate for last N days (default: 7)',
        )
        parser.add_argument(
            '--weekly',
            action='store_true',
            help='Also calculate weekly stats',
        )

    def handle(self, *args, **options):
        date_str = options.get('date')
        user_email = options.get('user')
        days = options.get('days', 7)
        calculate_weekly = options.get('weekly', False)

        # Determine target date
        if date_str:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            target_date = timezone.now().date()

        # Determine users
        if user_email:
            users = User.objects.filter(email=user_email)
        else:
            users = User.objects.all()

        total_users = users.count()
        self.stdout.write(f'Calculating analytics for {total_users} users...')

        # Calculate daily stats
        for i in range(days):
            calc_date = target_date - timedelta(days=i)
            self.calculate_daily_stats(users, calc_date)

        # Calculate weekly stats if requested
        if calculate_weekly:
            self.calculate_weekly_stats(users, target_date)

        self.stdout.write(
            self.style.SUCCESS(f'Analytics calculated successfully for {total_users} users')
        )

    def calculate_daily_stats(self, users, calc_date):
        """Calculate daily statistics for given users and date."""
        for user in users:
            daily_stats, created = DailyStats.objects.get_or_create(
                user=user,
                date=calc_date,
                defaults={
                    'tasks_created': 0,
                    'tasks_completed': 0,
                    'tasks_overdue': 0,
                    'hours_worked': Decimal('0.00'),
                    'productivity_score': Decimal('0.00'),
                    'categories_data': {}
                }
            )

            # Get all user tasks
            tasks = Task.objects.filter(user=user)

            # Calculate task counts
            daily_stats.tasks_created = tasks.filter(created_at__date=calc_date).count()
            daily_stats.tasks_completed = tasks.filter(
                status=Task.Status.COMPLETED,
                completed_at__date=calc_date
            ).count()
            daily_stats.tasks_overdue = tasks.filter(
                due_date__date__lt=calc_date,
                status__in=[Task.Status.PENDING, Task.Status.IN_PROGRESS]
            ).count()

            # Calculate hours worked (if actual_hours are tracked)
            completed_tasks = tasks.filter(
                status=Task.Status.COMPLETED,
                completed_at__date=calc_date,
                actual_hours__isnull=False
            )
            total_hours = sum(task.actual_hours for task in completed_tasks if task.actual_hours)
            daily_stats.hours_worked = Decimal(str(total_hours))

            # Calculate productivity score
            if daily_stats.tasks_created > 0:
                completion_rate = (daily_stats.tasks_completed / daily_stats.tasks_created) * 100
                daily_stats.productivity_score = Decimal(str(min(completion_rate, 100.0)))
            else:
                daily_stats.productivity_score = Decimal('0.00')

            # Calculate category-wise data
            categories_data = {}
            for task in tasks.filter(created_at__date=calc_date).select_related('category'):
                if task.category:
                    category_id = str(task.category.id)
                    if category_id not in categories_data:
                        categories_data[category_id] = {
                            'name': task.category.name,
                            'color': task.category.color,
                            'tasks_created': 0,
                            'tasks_completed': 0
                        }
                    categories_data[category_id]['tasks_created'] += 1

            # Count completed tasks by category for this date
            for task in tasks.filter(
                status=Task.Status.COMPLETED,
                completed_at__date=calc_date
            ).select_related('category'):
                if task.category:
                    category_id = str(task.category.id)
                    if category_id in categories_data:
                        categories_data[category_id]['tasks_completed'] += 1

            daily_stats.categories_data = categories_data
            daily_stats.save()

            if created:
                self.stdout.write(f'Created daily stats for {user.email} on {calc_date}')
            else:
                self.stdout.write(f'Updated daily stats for {user.email} on {calc_date}')

    def calculate_weekly_stats(self, users, end_date):
        """Calculate weekly statistics for given users."""
        # Calculate week boundaries
        week_start = end_date - timedelta(days=end_date.weekday())
        week_end = week_start + timedelta(days=6)
        year = end_date.year
        week_number = end_date.isocalendar()[1]

        for user in users:
            weekly_stats, created = WeeklyStats.objects.get_or_create(
                user=user,
                year=year,
                week_number=week_number,
                defaults={
                    'start_date': week_start,
                    'end_date': week_end,
                    'total_tasks_created': 0,
                    'total_tasks_completed': 0,
                    'total_tasks_overdue': 0,
                    'total_hours_worked': Decimal('0.00'),
                    'average_productivity_score': Decimal('0.00'),
                    'weekly_categories_data': {},
                    'daily_breakdown': []
                }
            )

            # Aggregate from daily stats
            daily_stats_qs = DailyStats.objects.filter(
                user=user,
                date__range=[week_start, week_end]
            )

            # Calculate totals
            weekly_stats.total_tasks_created = sum(ds.tasks_created for ds in daily_stats_qs)
            weekly_stats.total_tasks_completed = sum(ds.tasks_completed for ds in daily_stats_qs)
            weekly_stats.total_tasks_overdue = sum(ds.tasks_overdue for ds in daily_stats_qs)
            weekly_stats.total_hours_worked = sum(ds.hours_worked for ds in daily_stats_qs)

            # Calculate average productivity score
            productivity_scores = [ds.productivity_score for ds in daily_stats_qs if ds.productivity_score > 0]
            if productivity_scores:
                weekly_stats.average_productivity_score = Decimal(str(
                    sum(productivity_scores) / len(productivity_scores)
                ))
            else:
                weekly_stats.average_productivity_score = Decimal('0.00')

            # Aggregate category data
            weekly_categories = {}
            for daily_stat in daily_stats_qs:
                for cat_id, cat_data in daily_stat.categories_data.items():
                    if cat_id not in weekly_categories:
                        weekly_categories[cat_id] = {
                            'name': cat_data['name'],
                            'color': cat_data['color'],
                            'tasks_created': 0,
                            'tasks_completed': 0
                        }
                    weekly_categories[cat_id]['tasks_created'] += cat_data['tasks_created']
                    weekly_categories[cat_id]['tasks_completed'] += cat_data['tasks_completed']

            weekly_stats.weekly_categories_data = weekly_categories

            # Create daily breakdown
            daily_breakdown = []
            for i in range(7):
                check_date = week_start + timedelta(days=i)
                daily_stat = daily_stats_qs.filter(date=check_date).first()
                if daily_stat:
                    daily_breakdown.append({
                        'date': check_date.isoformat(),
                        'tasks_created': daily_stat.tasks_created,
                        'tasks_completed': daily_stat.tasks_completed,
                        'productivity_score': float(daily_stat.productivity_score)
                    })
                else:
                    daily_breakdown.append({
                        'date': check_date.isoformat(),
                        'tasks_created': 0,
                        'tasks_completed': 0,
                        'productivity_score': 0.0
                    })

            weekly_stats.daily_breakdown = daily_breakdown
            weekly_stats.save()

            if created:
                self.stdout.write(f'Created weekly stats for {user.email} (Week {week_number}, {year})')
            else:
                self.stdout.write(f'Updated weekly stats for {user.email} (Week {week_number}, {year})')
