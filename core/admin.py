from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import SystemSettings, ActivityLog, Notification


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    """Admin for SystemSettings model."""

    list_display = ['key', 'category', 'value_preview', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['key', 'value', 'description', 'category']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['category', 'key']

    fieldsets = (
        ('Setting Info', {'fields': ('key', 'category', 'description')}),
        ('Value', {'fields': ('value', 'is_active')}),
        ('Metadata', {'fields': ('id', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def value_preview(self, obj):
        """Display first 50 characters of value."""
        return obj.value[:50] + '...' if len(obj.value) > 50 else obj.value
    value_preview.short_description = 'Value Preview'

    actions = ['activate_settings', 'deactivate_settings']

    def activate_settings(self, request, queryset):
        """Activate selected settings."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} settings activated.')
    activate_settings.short_description = "Activate selected settings"

    def deactivate_settings(self, request, queryset):
        """Deactivate selected settings."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} settings deactivated.')
    deactivate_settings.short_description = "Deactivate selected settings"


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    """Admin for ActivityLog model."""

    list_display = ['user', 'action', 'resource_type', 'resource_id', 'ip_address', 'created_at']
    list_filter = ['action', 'resource_type', 'created_at']
    search_fields = ['user__email', 'resource_type', 'resource_id', 'description', 'ip_address']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Activity Info', {'fields': ('user', 'action', 'resource_type', 'resource_id')}),
        ('Description', {'fields': ('description',)}),
        ('Request Info', {'fields': ('ip_address', 'user_agent')}),
        ('Additional Data', {'fields': ('metadata',), 'classes': ('collapse',)}),
        ('Metadata', {'fields': ('id', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def has_add_permission(self, request):
        """Prevent manual addition of activity logs."""
        return False

    def has_change_permission(self, request, obj=None):
        """Make activity logs read-only."""
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin for Notification model."""

    list_display = [
        'recipient', 'title', 'notification_type', 'is_read_display',
        'created_at', 'read_at'
    ]
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['recipient__email', 'title', 'message']
    readonly_fields = ['id', 'created_at', 'updated_at', 'read_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Recipient & Type', {'fields': ('recipient', 'notification_type')}),
        ('Content', {'fields': ('title', 'message', 'action_url')}),
        ('Status', {'fields': ('is_read', 'read_at')}),
        ('Related Object', {
            'fields': ('related_object_type', 'related_object_id'),
            'classes': ('collapse',)
        }),
        ('Additional Data', {'fields': ('metadata',), 'classes': ('collapse',)}),
        ('Metadata', {'fields': ('id', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def is_read_display(self, obj):
        """Display read status with color coding."""
        if obj.is_read:
            return format_html('<span style="color: green;">✓ Read</span>')
        return format_html('<span style="color: red; font-weight: bold;">✗ Unread</span>')
    is_read_display.short_description = 'Status'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('recipient')

    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        """Mark selected notifications as read."""
        from django.utils import timezone
        unread_notifications = queryset.filter(is_read=False)
        updated = unread_notifications.update(is_read=True, read_at=timezone.now())
        self.message_user(request, f'{updated} notifications marked as read.')
    mark_as_read.short_description = "Mark selected notifications as read"

    def mark_as_unread(self, request, queryset):
        """Mark selected notifications as unread."""
        updated = queryset.update(is_read=False, read_at=None)
        self.message_user(request, f'{updated} notifications marked as unread.')
    mark_as_unread.short_description = "Mark selected notifications as unread"


# Customize admin site
admin.site.site_header = "Acta Task Management Admin"
admin.site.site_title = "Acta Admin Portal"
admin.site.index_title = "Welcome to Acta Administration"
