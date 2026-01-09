from django.db import models
from django.utils import timezone
import uuid


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides created_at and updated_at timestamps.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """
    Abstract base model that provides UUID primary key.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class BaseModel(TimeStampedModel, UUIDModel):
    """
    Abstract base model combining UUID and timestamp functionality.
    """
    class Meta:
        abstract = True


class SoftDeleteManager(models.Manager):
    """
    Custom manager to exclude soft deleted objects by default.
    """
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class SoftDeleteModel(models.Model):
    """
    Abstract model that provides soft delete functionality.
    """
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()  # Manager that includes deleted objects

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        """
        Soft delete the object by setting deleted_at timestamp.
        """
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self, *args, **kwargs):
        """
        Permanently delete the object from database.
        """
        super().delete(*args, **kwargs)

    def restore(self):
        """
        Restore a soft deleted object.
        """
        self.deleted_at = None
        self.save()

    @property
    def is_deleted(self):
        """
        Check if the object is soft deleted.
        """
        return self.deleted_at is not None


class AuditModel(BaseModel):
    """
    Abstract model that provides audit trail functionality.
    """
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created'
    )
    updated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated'
    )

    class Meta:
        abstract = True


class SystemSettings(BaseModel):
    """
    Model for storing system-wide configuration settings.
    """
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    category = models.CharField(max_length=50, default='general')

    class Meta:
        db_table = 'core_system_settings'
        verbose_name = 'System Setting'
        verbose_name_plural = 'System Settings'
        ordering = ['category', 'key']

    def __str__(self):
        return f"{self.key}: {self.value[:50]}"


class ActivityLog(BaseModel):
    """
    Model for logging user activities and system events.
    """
    class ActionType(models.TextChoices):
        CREATE = 'create', 'Create'
        UPDATE = 'update', 'Update'
        DELETE = 'delete', 'Delete'
        LOGIN = 'login', 'Login'
        LOGOUT = 'logout', 'Logout'
        VIEW = 'view', 'View'
        EXPORT = 'export', 'Export'
        IMPORT = 'import', 'Import'

    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='activity_logs',
        null=True,
        blank=True
    )
    action = models.CharField(max_length=20, choices=ActionType.choices)
    resource_type = models.CharField(max_length=50)  # Model name
    resource_id = models.CharField(max_length=100, blank=True)  # Object ID
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'core_activity_log'
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action', 'resource_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        user_info = self.user.email if self.user else 'Anonymous'
        return f"{user_info} - {self.action} {self.resource_type}"


class Notification(BaseModel):
    """
    Model for storing user notifications.
    """
    class NotificationType(models.TextChoices):
        TASK_ASSIGNED = 'task_assigned', 'Task Assigned'
        TASK_DUE = 'task_due', 'Task Due'
        TASK_OVERDUE = 'task_overdue', 'Task Overdue'
        TASK_COMPLETED = 'task_completed', 'Task Completed'
        COMMENT_ADDED = 'comment_added', 'Comment Added'
        SYSTEM = 'system', 'System Notification'

    recipient = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, blank=True)
    related_object_id = models.CharField(max_length=100, blank=True)
    action_url = models.URLField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'core_notification'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.recipient.email} - {self.title}"

    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
