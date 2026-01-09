"""
Custom permissions for Acta.
"""
from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Object-level permission to only allow owners to access their objects."""

    def has_object_permission(self, request, view, obj):
        """Check if the user is the owner of the object."""
        # Check if object has 'user' attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        # Check if object has 'owner' attribute
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        # Check if object is the user itself
        if hasattr(obj, 'email') and hasattr(request.user, 'email'):
            return obj == request.user
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allow read access to all authenticated users, write access only to owner."""

    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Allow read access to all, write access only to owner."""
        # Read permissions are allowed for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only to the owner of the object
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False


class IsAdminUser(permissions.BasePermission):
    """Allow access only to admin users."""

    def has_permission(self, request, view):
        """Check if user is an admin."""
        return (
            request.user and
            request.user.is_authenticated and
            (
                request.user.is_superuser or
                (hasattr(request.user, 'role') and
                 getattr(request.user.role, 'role', None) == 'admin')
            )
        )


class IsManagerOrAdmin(permissions.BasePermission):
    """Allow access to managers and admin users."""

    def has_permission(self, request, view):
        """Check if user is a manager or admin."""
        if not (request.user and request.user.is_authenticated):
            return False

        if request.user.is_superuser:
            return True

        if hasattr(request.user, 'role'):
            user_role = getattr(request.user.role, 'role', None)
            return user_role in ['admin', 'manager']

        return False


class IsProfileOwnerOrReadOnly(permissions.BasePermission):
    """Allow users to edit their own profile, read access to others."""

    def has_object_permission(self, request, view, obj):
        """Check profile ownership for write operations."""
        # Read permissions for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Write permissions only for profile owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user


class IsTaskOwnerOrAssigned(permissions.BasePermission):
    """Allow access to task owner or assigned user."""

    def has_object_permission(self, request, view, obj):
        """Check if user is task owner or assigned to the task."""
        if not (request.user and request.user.is_authenticated):
            return False

        # Task owner has full access
        if hasattr(obj, 'user') and obj.user == request.user:
            return True

        # Assigned user has read access and can update status/progress
        if hasattr(obj, 'assigned_to') and obj.assigned_to == request.user:
            # Allow read operations and status updates
            if request.method in permissions.SAFE_METHODS:
                return True
            # Allow PATCH for status updates
            if request.method == 'PATCH' and view.action in ['update_status', 'partial_update']:
                return True

        return False


class CanCreateTask(permissions.BasePermission):
    """Permission to create tasks based on user role."""

    def has_permission(self, request, view):
        """Check if user can create tasks."""
        if not (request.user and request.user.is_authenticated):
            return False

        # Allow task creation for all authenticated users by default
        # Can be customized based on user roles if needed
        if hasattr(request.user, 'role'):
            user_role = getattr(request.user.role, 'role', 'member')
            # Viewers cannot create tasks
            return user_role != 'viewer'

        return True


class CanManageUsers(permissions.BasePermission):
    """Permission to manage users - admin only."""

    def has_permission(self, request, view):
        """Check if user can manage other users."""
        return (
            request.user and
            request.user.is_authenticated and
            (
                request.user.is_superuser or
                (hasattr(request.user, 'role') and
                 getattr(request.user.role, 'role', None) == 'admin')
            )
        )


class CanViewAnalytics(permissions.BasePermission):
    """Permission to view analytics data."""

    def has_permission(self, request, view):
        """Check if user can view analytics."""
        if not (request.user and request.user.is_authenticated):
            return False

        # All authenticated users can view their own analytics
        return True

    def has_object_permission(self, request, view, obj):
        """Check if user can view specific analytics object."""
        # Users can only view their own analytics
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False
