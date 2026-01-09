"""
Signals for tasks app.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Task


@receiver(pre_save, sender=Task)
def handle_task_completion(sender, instance, **kwargs):
    """Handle task status changes."""
    if instance.pk:
        try:
            old_task = Task.objects.get(pk=instance.pk)
            # Task just completed
            if old_task.status != Task.Status.COMPLETED and instance.status == Task.Status.COMPLETED:
                instance.completed_at = timezone.now()
            # Task uncompleted
            elif old_task.status == Task.Status.COMPLETED and instance.status != Task.Status.COMPLETED:
                instance.completed_at = None
        except Task.DoesNotExist:
            pass


@receiver(post_save, sender=Task)
def update_analytics_on_task_change(sender, instance, created, **kwargs):
    """Update analytics when tasks are created or completed."""
    from analytics.models import DailyStats
    from decimal import Decimal

    today = timezone.now().date()
    daily_stats, stats_created = DailyStats.objects.get_or_create(
        user=instance.user,
        date=today,
        defaults={
            'tasks_created': 0,
            'tasks_completed': 0,
            'tasks_overdue': 0,
            'hours_worked': Decimal('0.00'),
            'productivity_score': Decimal('0.00'),
            'categories_data': {}
        }
    )

    if created:
        # New task created
        daily_stats.tasks_created += 1

    # Check if task was completed today
    if instance.status == Task.Status.COMPLETED and instance.completed_at:
        if instance.completed_at.date() == today:
            # Recalculate completed tasks for today
            completed_today = Task.objects.filter(
                user=instance.user,
                status=Task.Status.COMPLETED,
                completed_at__date=today
            ).count()
            daily_stats.tasks_completed = completed_today

    # Update productivity score
    if daily_stats.tasks_created > 0:
        completion_rate = (daily_stats.tasks_completed / daily_stats.tasks_created) * 100
        daily_stats.productivity_score = Decimal(str(min(completion_rate, 100.0)))

    daily_stats.save()


@receiver(post_save, sender=Task)
def update_category_analytics(sender, instance, created, **kwargs):
    """Update category-specific analytics when tasks change."""
    if instance.category:
        today = timezone.now().date()

        try:
            from analytics.models import DailyStats as DS
            daily_stats = DS.objects.get(user=instance.user, date=today)

            # Get or initialize category data
            categories_data = daily_stats.categories_data or {}
            category_id = str(instance.category.id)

            if category_id not in categories_data:
                categories_data[category_id] = {
                    'name': instance.category.name,
                    'color': instance.category.color,
                    'tasks_created': 0,
                    'tasks_completed': 0
                }

            if created:
                categories_data[category_id]['tasks_created'] += 1

            # Update completed count for this category
            completed_count = Task.objects.filter(
                user=instance.user,
                category=instance.category,
                status=Task.Status.COMPLETED,
                completed_at__date=today
            ).count()
            categories_data[category_id]['tasks_completed'] = completed_count

            daily_stats.categories_data = categories_data
            daily_stats.save()

        except DS.DoesNotExist:
            pass
