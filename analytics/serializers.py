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
            'tasks_overdue', 'hours_worked', 'productivity_score',
            'categories_data', 'completion_rate', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_completion_rate(self, obj):
        return float(obj.completion_rate)


class WeeklyStatsSerializer(serializers.ModelSerializer):
    """Serializer for weekly statistics."""

    completion_rate = serializers.SerializerMethodField()

    class Meta:
        model = WeeklyStats
        fields = [
            'id', 'year', 'week_number', 'start_date', 'end_date',
            'total_tasks_created', 'total_tasks_completed', 'total_tasks_overdue',
            'total_hours_worked', 'average_productivity_score',
            'weekly_categories_data', 'daily_breakdown', 'completion_rate',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_completion_rate(self, obj):
        return float(obj.completion_rate)


class OverviewStatsSerializer(serializers.Serializer):
    """Serializer for overview dashboard statistics."""

    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    pending_tasks = serializers.IntegerField()
    in_progress_tasks = serializers.IntegerField()
    cancelled_tasks = serializers.IntegerField()
    overdue_tasks = serializers.IntegerField()
    due_today = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    tasks_this_week = serializers.IntegerField()
    completed_this_week = serializers.IntegerField()
    productivity_score = serializers.FloatField()


class ProductivityTrendSerializer(serializers.Serializer):
    """Serializer for productivity trends."""

    date = serializers.DateField()
    tasks_created = serializers.IntegerField()
    tasks_completed = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    productivity_score = serializers.FloatField()


class CategoryStatsSerializer(serializers.Serializer):
    """Serializer for category-wise statistics."""

    category_id = serializers.UUIDField()
    category_name = serializers.CharField()
    category_color = serializers.CharField()
    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    pending_tasks = serializers.IntegerField()
    overdue_tasks = serializers.IntegerField()
    completion_rate = serializers.FloatField()
