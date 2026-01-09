"""Task URLs with nested routes."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, CategoryViewSet, TaskCommentViewSet, TaskAttachmentViewSet

# Main router
router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'categories', CategoryViewSet, basename='category')

# Additional task-specific URLs for nested resources
task_patterns = [
    path('tasks/<uuid:task_pk>/comments/', TaskCommentViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='task-comments-list'),
    path('tasks/<uuid:task_pk>/comments/<uuid:pk>/', TaskCommentViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='task-comments-detail'),
    path('tasks/<uuid:task_pk>/attachments/', TaskAttachmentViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='task-attachments-list'),
    path('tasks/<uuid:task_pk>/attachments/<uuid:pk>/', TaskAttachmentViewSet.as_view({
        'get': 'retrieve',
        'delete': 'destroy'
    }), name='task-attachments-detail'),
]

urlpatterns = [
    path('', include(router.urls)),
] + task_patterns
