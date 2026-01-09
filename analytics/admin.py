from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import DailyStats, WeeklyStats


@admin.register(DailyStats)
class DailyStatsAdmin(admin.ModelAdmin):
    """Admin for DailyStats model."""

    list_display = [
        'user', 'date', 'tasks_created', 'tasks_completed',
        'completion_rate_display', 'productivity_score', 'created_at'
    ]
    list_filter = ['date', 'created_at', 'user']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at', 'completion_rate_display']
    ordering = ['-date']
    date_hierarchy = 'date'

    fieldsets = (
        ('User & Date', {'fields': ('user', 'date')}),
        ('Task Statistics', {
            'fields': ('tasks_created', 'tasks_completed', 'tasks_overdue')
        }),
        ('Performance Metrics', {
            'fields': ('hours_worked', 'productivity_score', 'completion_rate_display')
        }),
        ('Additional Data', {
            'fields': ('categories_data',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def completion_rate_display(self, obj):
        """Display completion rate with color coding."""
        rate = float(obj.completion_rate)
        if rate >= 80:
            color = 'green'
        elif rate >= 60:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, rate
        )
    completion_rate_display.short_description = 'Completion Rate'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(WeeklyStats)
class WeeklyStatsAdmin(admin.ModelAdmin):
    """Admin for WeeklyStats model."""

    list_display = [
        'user', 'week_display', 'total_tasks_created', 'total_tasks_completed',
        'completion_rate_display', 'average_productivity_score', 'created_at'
    ]
    list_filter = ['year', 'week_number', 'created_at', 'user']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at', 'completion_rate_display']
    ordering = ['-year', '-week_number']

    fieldsets = (
        ('User & Period', {'fields': ('user', 'year', 'week_number', 'start_date', 'end_date')}),
        ('Task Statistics', {
            'fields': ('total_tasks_created', 'total_tasks_completed', 'total_tasks_overdue')
        }),
        ('Performance Metrics', {
            'fields': ('total_hours_worked', 'average_productivity_score', 'completion_rate_display')
        }),
        ('Additional Data', {
            'fields': ('weekly_categories_data', 'daily_breakdown'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def week_display(self, obj):
        """Display week information in readable format."""
        return f"Week {obj.week_number}, {obj.year}"
    week_display.short_description = 'Week'

    def completion_rate_display(self, obj):
        """Display completion rate with color coding."""
        rate = float(obj.completion_rate)
        if rate >= 80:
            color = 'green'
        elif rate >= 60:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, rate
        )
    completion_rate_display.short_description = 'Completion Rate'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


# Custom admin site configuration
admin.site.site_header = "Acta Task Management Admin"
admin.site.site_title = "Acta Admin"
admin.site.index_title = "Welcome to Acta Administration"
