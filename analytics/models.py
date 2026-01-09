from django.db import models
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
import uuid


class DailyStats(models.Model):
    """Daily statistics for user productivity tracking."""

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
    hours_worked = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00')
    )
    productivity_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Calculated productivity score based on various metrics"
    )
    categories_data = models.JSONField(
        default=dict,
        help_text="Category-wise task distribution and completion data"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'analytics_daily_stats'
        verbose_name = 'Daily Stats'
        verbose_name_plural = 'Daily Stats'
        unique_together = ['user', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.date}"

    @property
    def completion_rate(self):
        """Calculate task completion rate for the day."""
        if self.tasks_created == 0:
            return Decimal('0.00')
        return Decimal(self.tasks_completed / self.tasks_created * 100).quantize(Decimal('0.01'))


class WeeklyStats(models.Model):
    """Weekly statistics aggregated from daily stats."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='weekly_stats'
    )
    year = models.PositiveIntegerField()
    week_number = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    total_tasks_created = models.PositiveIntegerField(default=0)
    total_tasks_completed = models.PositiveIntegerField(default=0)
    total_tasks_overdue = models.PositiveIntegerField(default=0)
    total_hours_worked = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0.00')
    )
    average_productivity_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00')
    )
    weekly_categories_data = models.JSONField(
        default=dict,
        help_text="Weekly aggregated category data"
    )
    daily_breakdown = models.JSONField(
        default=list,
        help_text="Daily stats breakdown for the week"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'analytics_weekly_stats'
        verbose_name = 'Weekly Stats'
        verbose_name_plural = 'Weekly Stats'
        unique_together = ['user', 'year', 'week_number']
        ordering = ['-year', '-week_number']
        indexes = [
            models.Index(fields=['user', 'year', 'week_number']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        return f"{self.user.email} - Week {self.week_number}, {self.year}"

    @property
    def completion_rate(self):
        """Calculate weekly task completion rate."""
        if self.total_tasks_created == 0:
            return Decimal('0.00')
        return Decimal(self.total_tasks_completed / self.total_tasks_created * 100).quantize(Decimal('0.01'))
