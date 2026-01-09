"""
Views for tasks.
"""
from rest_framework import viewsets, status, generics, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta

from .models import Task, Category, TaskComment, TaskAttachment
from .serializers import (
    TaskListSerializer,
    TaskDetailSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer,
    TaskStatusUpdateSerializer,
    BulkTaskActionSerializer,
    CategorySerializer,
    TaskCommentSerializer,
    TaskAttachmentSerializer,
)
from .filters import TaskFilter
from core.permissions import IsOwner, IsTaskOwnerOrAssigned, CanCreateTask


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tasks.

    list: Get all tasks for the current user
    create: Create a new task
    retrieve: Get a specific task
    update: Update a task
    partial_update: Partially update a task
    destroy: Delete a task
    """

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TaskFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'priority', 'status']
    ordering = ['-created_at']
    permission_classes = [permissions.IsAuthenticated, IsTaskOwnerOrAssigned]

    def get_queryset(self):
        """Return tasks for the current user."""
        return Task.objects.filter(user=self.request.user).select_related('category', 'assigned_to')

    def get_permissions(self):
        """Return appropriate permissions based on action."""
        if self.action == 'create':
            return [permissions.IsAuthenticated(), CanCreateTask()]
        elif self.action in ['list']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsTaskOwnerOrAssigned()]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return TaskListSerializer
        elif self.action == 'create':
            return TaskCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TaskUpdateSerializer
        return TaskDetailSerializer

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get tasks due today."""
        today = timezone.now().date()
        tasks = self.get_queryset().filter(due_date__date=today)
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue tasks."""
        today = timezone.now().date()
        tasks = self.get_queryset().filter(
            due_date__date__lt=today,
            status__in=[Task.Status.PENDING, Task.Status.IN_PROGRESS]
        )
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def completed(self, request):
        """Get tasks completed in the last 7 days."""
        seven_days_ago = timezone.now() - timedelta(days=7)
        tasks = self.get_queryset().filter(
            status=Task.Status.COMPLETED,
            completed_at__gte=seven_days_ago
        ).order_by('-completed_at')
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming tasks (next 7 days)."""
        today = timezone.now().date()
        next_week = today + timedelta(days=7)
        tasks = self.get_queryset().filter(
            due_date__date__gte=today,
            due_date__date__lte=next_week,
            status__in=[Task.Status.PENDING, Task.Status.IN_PROGRESS]
        ).order_by('due_date')
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Quick status update for a task."""
        task = self.get_object()
        serializer = TaskStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task.status = serializer.validated_data['status']
        task.save()

        return Response(TaskDetailSerializer(task).data)

    @action(detail=True, methods=['post'])
    def toggle_complete(self, request, pk=None):
        """Toggle task completion status."""
        task = self.get_object()

        if task.status == Task.Status.COMPLETED:
            task.status = Task.Status.PENDING
            task.completed_at = None
        else:
            task.status = Task.Status.COMPLETED
            task.completed_at = timezone.now()

        task.save()
        return Response(TaskDetailSerializer(task).data)

    @action(detail=False, methods=['post'])
    def bulk_action(self, request):
        """Perform bulk actions on multiple tasks."""
        serializer = BulkTaskActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task_ids = serializer.validated_data['task_ids']
        action = serializer.validated_data['action']
        value = serializer.validated_data.get('value')

        tasks = self.get_queryset().filter(id__in=task_ids)

        if action == 'complete':
            tasks.update(status=Task.Status.COMPLETED, completed_at=timezone.now())
        elif action == 'delete':
            tasks.delete()
            return Response({'message': f'{len(task_ids)} tasks deleted'})
        elif action == 'change_priority' and value:
            tasks.update(priority=value)
        elif action == 'change_status' and value:
            tasks.update(status=value)

        return Response({'message': f'Bulk action "{action}" applied to {len(task_ids)} tasks'})


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing task categories."""

    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


class TaskCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing task comments."""

    serializer_class = TaskCommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        task_id = self.kwargs.get('task_pk')
        return TaskComment.objects.filter(
            task_id=task_id,
            task__user=self.request.user
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['task_id'] = self.kwargs.get('task_pk')
        return context


class TaskAttachmentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing task attachments."""

    serializer_class = TaskAttachmentSerializer
    parser_classes = [MultiPartParser, FormParser]
    http_method_names = ['get', 'post', 'delete']  # No updates for attachments
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        task_id = self.kwargs.get('task_pk')
        return TaskAttachment.objects.filter(
            task_id=task_id,
            task__user=self.request.user
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['task_id'] = self.kwargs.get('task_pk')
        return context
