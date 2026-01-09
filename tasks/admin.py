from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Category, Task, TaskComment, TaskAttachment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin for Category model."""

    list_display = ['name', 'user', 'color_display', 'task_count', 'is_default', 'created_at']
    list_filter = ['is_default', 'created_at', 'user']
    search_fields = ['name', 'description', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']

    fieldsets = (
        ('Category Info', {'fields': ('name', 'description', 'user')}),
        ('Display', {'fields': ('color', 'icon', 'is_default')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def color_display(self, obj):
        """Display color as a colored box."""
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc;"></div>',
            obj.color
        )
    color_display.short_description = 'Color'

    def task_count(self, obj):
        """Display number of tasks in this category."""
        count = obj.tasks.count()
        if count > 0:
            url = reverse('admin:tasks_task_changelist') + f'?category__id__exact={obj.id}'
            return format_html('<a href="{}">{} tasks</a>', url, count)
        return '0 tasks'
    task_count.short_description = 'Tasks'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin for Task model."""

    list_display = [
        'title', 'user', 'status', 'priority', 'category',
        'due_date', 'is_overdue_display', 'created_at'
    ]
    list_filter = [
        'status', 'priority', 'category', 'is_recurring',
        'created_at', 'due_date', 'user'
    ]
    search_fields = ['title', 'description', 'user__email', 'tags']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Task Info', {
            'fields': ('title', 'description', 'user', 'assigned_to')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'category')
        }),
        ('Dates & Time', {
            'fields': ('due_date', 'start_date', 'completed_at', 'estimated_hours', 'actual_hours')
        }),
        ('Organization', {
            'fields': ('tags', 'parent_task', 'position')
        }),
        ('Recurrence', {
            'fields': ('is_recurring', 'recurrence_pattern'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def is_overdue_display(self, obj):
        """Display overdue status with color coding."""
        if obj.is_overdue:
            return format_html('<span style="color: red; font-weight: bold;">Yes</span>')
        return format_html('<span style="color: green;">No</span>')
    is_overdue_display.short_description = 'Overdue'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'assigned_to', 'category', 'parent_task')

    actions = ['mark_completed', 'mark_pending', 'mark_in_progress']

    def mark_completed(self, request, queryset):
        """Mark selected tasks as completed."""
        from django.utils import timezone
        updated = queryset.update(status=Task.Status.COMPLETED, completed_at=timezone.now())
        self.message_user(request, f'{updated} tasks marked as completed.')
    mark_completed.short_description = "Mark selected tasks as completed"

    def mark_pending(self, request, queryset):
        """Mark selected tasks as pending."""
        updated = queryset.update(status=Task.Status.PENDING, completed_at=None)
        self.message_user(request, f'{updated} tasks marked as pending.')
    mark_pending.short_description = "Mark selected tasks as pending"

    def mark_in_progress(self, request, queryset):
        """Mark selected tasks as in progress."""
        updated = queryset.update(status=Task.Status.IN_PROGRESS, completed_at=None)
        self.message_user(request, f'{updated} tasks marked as in progress.')
    mark_in_progress.short_description = "Mark selected tasks as in progress"


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    """Admin for TaskComment model."""

    list_display = ['task', 'user', 'content_preview', 'is_internal', 'created_at']
    list_filter = ['is_internal', 'created_at', 'user']
    search_fields = ['content', 'task__title', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Comment Info', {'fields': ('task', 'user', 'content')}),
        ('Settings', {'fields': ('is_internal',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def content_preview(self, obj):
        """Display first 50 characters of content."""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('task', 'user')


@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    """Admin for TaskAttachment model."""

    list_display = ['file_name', 'task', 'user', 'file_type', 'file_size_display', 'uploaded_at']
    list_filter = ['file_type', 'uploaded_at', 'user']
    search_fields = ['file_name', 'task__title', 'user__email']
    readonly_fields = ['uploaded_at', 'file_size', 'file_type']
    ordering = ['-uploaded_at']

    fieldsets = (
        ('File Info', {'fields': ('task', 'user', 'file', 'file_name')}),
        ('File Details', {'fields': ('file_type', 'file_size')}),
        ('Timestamps', {'fields': ('uploaded_at',)}),
    )

    def file_size_display(self, obj):
        """Display file size in human readable format."""
        size = obj.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    file_size_display.short_description = 'File Size'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('task', 'user')
