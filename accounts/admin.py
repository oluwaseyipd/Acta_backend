from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User, Profile, UserRole


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom admin for User model."""

    list_display = ['email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['is_staff', 'is_active', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-date_joined']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

    readonly_fields = ['date_joined', 'last_login']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin for Profile model."""

    list_display = ['user', 'phone_number', 'location', 'timezone', 'created_at']
    list_filter = ['timezone', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'phone_number', 'location']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Contact Info', {'fields': ('phone_number', 'location', 'website')}),
        ('Personal Info', {'fields': ('bio', 'birth_date', 'avatar')}),
        ('Settings', {'fields': ('timezone', 'notification_preferences')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """Admin for UserRole model."""

    list_display = ['user', 'role', 'assigned_by', 'assigned_at']
    list_filter = ['role', 'assigned_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['assigned_at', 'updated_at']

    fieldsets = (
        ('Role Assignment', {'fields': ('user', 'role')}),
        ('Permissions', {'fields': ('permissions',)}),
        ('Assignment Info', {'fields': ('assigned_by', 'assigned_at', 'updated_at')}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'assigned_by')
