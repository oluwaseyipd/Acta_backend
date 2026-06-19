"""
Signals for accounts app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Profile, UserRole


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a profile, role and default categories when a new user is created."""
    if created:
        Profile.objects.create(user=instance)
        # Assign default user role
        UserRole.objects.create(user=instance, role=UserRole.RoleType.MEMBER)
        
        # Provision default categories
        from tasks.models import Category
        default_categories = [
            {'name': 'Work', 'color': '#3b82f6', 'icon': 'briefcase'},
            {'name': 'Personal', 'color': '#10b981', 'icon': 'user'},
            {'name': 'Health', 'color': '#ef4444', 'icon': 'heart'},
            {'name': 'Learning', 'color': '#8b5cf6', 'icon': 'book'},
            {'name': 'Finance', 'color': '#f59e0b', 'icon': 'dollar'},
        ]
        for cat in default_categories:
            Category.objects.get_or_create(
                user=instance,
                name=cat['name'],
                defaults={
                    'color': cat['color'],
                    'icon': cat['icon'],
                    'is_default': True
                }
            )


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    """Save profile when user is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()
