"""
Filters for tasks.
"""
import django_filters
from .models import Task


class TaskFilter(django_filters.FilterSet):
    """Filter for tasks."""

    # Exact matches
    status = django_filters.ChoiceFilter(choices=Task.Status.choices)
    priority = django_filters.ChoiceFilter(choices=Task.Priority.choices)
    category = django_filters.UUIDFilter(field_name='category__id')

    # Date filters
    due_date = django_filters.DateFilter()
    due_date__gte = django_filters.DateFilter(field_name='due_date', lookup_expr='gte')
    due_date__lte = django_filters.DateFilter(field_name='due_date', lookup_expr='lte')
    created_at__gte = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at__lte = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')

    # Boolean filters
    is_overdue = django_filters.BooleanFilter(method='filter_is_overdue')
    is_due_today = django_filters.BooleanFilter(method='filter_is_due_today')

    class Meta:
        model = Task
        fields = ['status', 'priority', 'category', 'due_date']

    def filter_is_overdue(self, queryset, name, value):
        from django.utils import timezone
        today = timezone.now().date()
        if value:
            return queryset.filter(
                due_date__lt=today,
                status__in=[Task.Status.PENDING, Task.Status.IN_PROGRESS]
            )
        return queryset.exclude(
            due_date__lt=today,
            status__in=[Task.Status.PENDING, Task.Status.IN_PROGRESS]
        )

    def filter_is_due_today(self, queryset, name, value):
        from django.utils import timezone
        today = timezone.now().date()
        if value:
            return queryset.filter(due_date=today)
        return queryset.exclude(due_date=today)
