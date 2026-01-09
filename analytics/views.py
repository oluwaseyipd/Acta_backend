"""
Views for analytics.
"""
from rest_framework import generics, views, permissions
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta

from tasks.models import Task, Category
from .models import DailyStats, WeeklyStats
from .serializers import (
    DailyStatsSerializer,
    WeeklyStatsSerializer,
    OverviewStatsSerializer,
    ProductivityTrendSerializer,
    CategoryStatsSerializer,
)
from core.permissions import CanViewAnalytics


class OverviewStatsView(views.APIView):
    """Get overview statistics for the dashboard."""

    permission_classes = [permissions.IsAuthenticated, CanViewAnalytics]

    def get(self, request):
        user = request.user
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())

        tasks = Task.objects.filter(user=user)

        stats = {
            'total_tasks': tasks.count(),
            'completed_tasks': tasks.filter(status=Task.Status.COMPLETED).count(),
            'pending_tasks': tasks.filter(status=Task.Status.PENDING).count(),
            'in_progress_tasks': tasks.filter(status=Task.Status.IN_PROGRESS).count(),
            'cancelled_tasks': tasks.filter(status=Task.Status.CANCELLED).count(),
            'overdue_tasks': tasks.filter(
                due_date__date__lt=today,
                status__in=[Task.Status.PENDING, Task.Status.IN_PROGRESS]
            ).count(),
            'due_today': tasks.filter(due_date__date=today).count(),
            'tasks_this_week': tasks.filter(created_at__date__gte=week_start).count(),
            'completed_this_week': tasks.filter(
                status=Task.Status.COMPLETED,
                completed_at__date__gte=week_start
            ).count(),
        }

        # Calculate completion rate
        if stats['total_tasks'] > 0:
            stats['completion_rate'] = round(
                (stats['completed_tasks'] / stats['total_tasks']) * 100, 1
            )
        else:
            stats['completion_rate'] = 0.0

        # Calculate productivity score (example calculation)
        stats['productivity_score'] = min(stats['completion_rate'], 100.0)

        serializer = OverviewStatsSerializer(stats)
        return Response(serializer.data)


class DailyStatsView(generics.ListAPIView):
    """Get daily statistics for the last N days."""

    serializer_class = DailyStatsSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewAnalytics]

    def get_queryset(self):
        days = int(self.request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)

        return DailyStats.objects.filter(
            user=self.request.user,
            date__gte=start_date
        ).order_by('date')


class WeeklyStatsView(generics.ListAPIView):
    """Get weekly statistics for the last N weeks."""

    serializer_class = WeeklyStatsSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewAnalytics]

    def get_queryset(self):
        weeks = int(self.request.query_params.get('weeks', 12))
        today = timezone.now().date()
        start_date = today - timedelta(weeks=weeks)

        return WeeklyStats.objects.filter(
            user=self.request.user,
            start_date__gte=start_date
        ).order_by('start_date')


class ProductivityTrendView(views.APIView):
    """Get productivity trends for charting."""

    permission_classes = [permissions.IsAuthenticated, CanViewAnalytics]

    def get(self, request):
        days = int(request.query_params.get('days', 14))
        today = timezone.now().date()

        trends = []
        for i in range(days - 1, -1, -1):
            date = today - timedelta(days=i)
            tasks = Task.objects.filter(user=request.user)

            created_count = tasks.filter(created_at__date=date).count()
            completed_count = tasks.filter(
                status=Task.Status.COMPLETED,
                completed_at__date=date
            ).count()

            completion_rate = 0.0
            if created_count > 0:
                completion_rate = round((completed_count / created_count) * 100, 1)

            trends.append({
                'date': date,
                'tasks_created': created_count,
                'tasks_completed': completed_count,
                'completion_rate': completion_rate,
                'productivity_score': min(completion_rate, 100.0)
            })

        serializer = ProductivityTrendSerializer(trends, many=True)
        return Response(serializer.data)


class CategoryStatsView(views.APIView):
    """Get statistics grouped by category."""

    permission_classes = [permissions.IsAuthenticated, CanViewAnalytics]

    def get(self, request):
        categories = Category.objects.filter(user=request.user).annotate(
            total_tasks=Count('tasks'),
            completed_tasks=Count('tasks', filter=Q(tasks__status=Task.Status.COMPLETED)),
            pending_tasks=Count('tasks', filter=Q(tasks__status=Task.Status.PENDING)),
            overdue_tasks=Count(
                'tasks',
                filter=Q(
                    tasks__due_date__date__lt=timezone.now().date(),
                    tasks__status__in=[Task.Status.PENDING, Task.Status.IN_PROGRESS]
                )
            )
        )

        stats = []
        for category in categories:
            completion_rate = 0.0
            if category.total_tasks > 0:
                completion_rate = round(
                    (category.completed_tasks / category.total_tasks) * 100, 1
                )

            stats.append({
                'category_id': category.id,
                'category_name': category.name,
                'category_color': category.color,
                'total_tasks': category.total_tasks,
                'completed_tasks': category.completed_tasks,
                'pending_tasks': category.pending_tasks,
                'overdue_tasks': category.overdue_tasks,
                'completion_rate': completion_rate,
            })

        serializer = CategoryStatsSerializer(stats, many=True)
        return Response(serializer.data)
