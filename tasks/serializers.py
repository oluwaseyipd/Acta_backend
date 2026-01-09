"""
Serializers for tasks.
"""
from rest_framework import serializers
from .models import Task, Category, TaskComment, TaskAttachment
from accounts.serializers import UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for task categories."""

    task_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'color', 'icon', 'is_default', 'task_count', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_task_count(self, obj):
        return obj.tasks.count()

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TaskCommentSerializer(serializers.ModelSerializer):
    """Serializer for task comments."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = TaskComment
        fields = ['id', 'user', 'content', 'is_internal', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['task_id'] = self.context['task_id']
        return super().create(validated_data)


class TaskAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for task attachments."""

    user = UserSerializer(source='user', read_only=True)

    class Meta:
        model = TaskAttachment
        fields = ['id', 'file', 'file_name', 'file_size', 'file_type', 'user', 'uploaded_at']
        read_only_fields = ['id', 'file_name', 'file_size', 'file_type', 'user', 'uploaded_at']

    def create(self, validated_data):
        file = validated_data['file']
        validated_data['file_name'] = file.name
        validated_data['file_size'] = file.size
        validated_data['file_type'] = file.content_type
        validated_data['user'] = self.context['request'].user
        validated_data['task_id'] = self.context['task_id']
        return super().create(validated_data)


class TaskListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for task lists."""

    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    is_due_today = serializers.BooleanField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'priority', 'status',
            'due_date', 'start_date', 'category', 'category_name', 'category_color',
            'is_overdue', 'is_due_today', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class TaskDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single task view."""

    user = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    assigned_to_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    comments = TaskCommentSerializer(many=True, read_only=True)
    attachments = TaskAttachmentSerializer(many=True, read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    is_due_today = serializers.BooleanField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'priority', 'status',
            'due_date', 'start_date', 'estimated_hours', 'actual_hours',
            'completed_at', 'tags',
            'user', 'category', 'category_id',
            'assigned_to', 'assigned_to_id',
            'is_recurring', 'recurrence_pattern',
            'parent_task', 'position',
            'is_overdue', 'is_due_today',
            'comments', 'attachments',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'completed_at', 'created_at', 'updated_at']


class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tasks."""

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'priority', 'status',
            'due_date', 'start_date', 'estimated_hours', 'tags',
            'category', 'assigned_to',
            'is_recurring', 'recurrence_pattern', 'parent_task'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TaskUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating tasks."""

    class Meta:
        model = Task
        fields = [
            'title', 'description', 'priority', 'status',
            'due_date', 'start_date', 'estimated_hours', 'actual_hours',
            'tags', 'category', 'assigned_to',
            'is_recurring', 'recurrence_pattern'
        ]


class TaskStatusUpdateSerializer(serializers.Serializer):
    """Serializer for quick status updates."""

    status = serializers.ChoiceField(choices=Task.Status.choices)


class BulkTaskActionSerializer(serializers.Serializer):
    """Serializer for bulk task operations."""

    task_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1
    )
    action = serializers.ChoiceField(choices=[
        ('complete', 'Mark as Completed'),
        ('delete', 'Delete'),
        ('change_priority', 'Change Priority'),
        ('change_status', 'Change Status'),
    ])
    value = serializers.CharField(required=False, allow_blank=True)
