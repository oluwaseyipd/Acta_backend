"""
Signals for accounts app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Profile, UserRole


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a profile when a new user is created."""
    if created:
        Profile.objects.create(user=instance)
        # Assign default user role
        UserRole.objects.create(user=instance, role=UserRole.RoleType.MEMBER)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    """Save profile when user is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()
