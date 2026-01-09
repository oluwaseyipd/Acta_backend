"""
Management command to clean up old analytics data.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from analytics.models import DailyStats, WeeklyStats

User = get_user_model()


class Command(BaseCommand):
    help = 'Clean up old analytics data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Keep analytics data for last N days (default: 90)',
        )
        parser.add_argument(
            '--weeks',
            type=int,
            default=52,
            help='Keep weekly analytics data for last N weeks (default: 52)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Actually perform the deletion (required for safety)',
        )

    def handle(self, *args, **options):
        days_to_keep = options['days']
        weeks_to_keep = options['weeks']
        dry_run = options['dry_run']
        confirm = options['confirm']

        if not dry_run and not confirm:
            self.stdout.write(
                self.style.WARNING(
                    'This command will permanently delete analytics data. '
                    'Use --dry-run to preview or --confirm to execute.'
                )
            )
            return

        # Calculate cutoff dates
        daily_cutoff_date = timezone.now().date() - timedelta(days=days_to_keep)
        weekly_cutoff_date = timezone.now().date() - timedelta(weeks=weeks_to_keep * 7)

        # Find old daily stats
        old_daily_stats = DailyStats.objects.filter(date__lt=daily_cutoff_date)
        daily_count = old_daily_stats.count()

        # Find old weekly stats
        old_weekly_stats = WeeklyStats.objects.filter(start_date__lt=weekly_cutoff_date)
        weekly_count = old_weekly_stats.count()

        self.stdout.write(f'Found {daily_count} daily stats records older than {daily_cutoff_date}')
        self.stdout.write(f'Found {weekly_count} weekly stats records older than {weekly_cutoff_date}')

        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN - No data will be deleted')
            )
            if daily_count > 0:
                self.stdout.write(f'Would delete {daily_count} daily stats records')
            if weekly_count > 0:
                self.stdout.write(f'Would delete {weekly_count} weekly stats records')
            return

        if not confirm:
            return

        # Perform actual deletion
        deleted_daily = 0
        deleted_weekly = 0

        if daily_count > 0:
            deleted_daily, _ = old_daily_stats.delete()
            self.stdout.write(
                self.style.SUCCESS(f'Deleted {deleted_daily} daily stats records')
            )

        if weekly_count > 0:
            deleted_weekly, _ = old_weekly_stats.delete()
            self.stdout.write(
                self.style.SUCCESS(f'Deleted {deleted_weekly} weekly stats records')
            )

        if deleted_daily == 0 and deleted_weekly == 0:
            self.stdout.write(
                self.style.SUCCESS('No old analytics data found to delete')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Cleanup completed: {deleted_daily} daily + {deleted_weekly} weekly records deleted'
                )
            )
