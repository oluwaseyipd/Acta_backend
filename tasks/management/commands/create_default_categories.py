"""
Management command to create default categories for all users.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tasks.models import Category

User = get_user_model()

DEFAULT_CATEGORIES = [
    {'name': 'Work', 'color': '#3b82f6', 'icon': 'briefcase'},
    {'name': 'Personal', 'color': '#10b981', 'icon': 'user'},
    {'name': 'Health', 'color': '#ef4444', 'icon': 'heart'},
    {'name': 'Learning', 'color': '#8b5cf6', 'icon': 'book'},
    {'name': 'Finance', 'color': '#f59e0b', 'icon': 'dollar'},
]


class Command(BaseCommand):
    help = 'Create default categories for all users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Create categories for specific user email',
        )

    def handle(self, *args, **options):
        user_email = options.get('user')

        if user_email:
            users = User.objects.filter(email=user_email)
        else:
            users = User.objects.all()

        for user in users:
            for cat_data in DEFAULT_CATEGORIES:
                category, created = Category.objects.get_or_create(
                    user=user,
                    name=cat_data['name'],
                    defaults={
                        'color': cat_data['color'],
                        'icon': cat_data['icon'],
                        'is_default': True,
                    }
                )
                if created:
                    self.stdout.write(f'Created category "{category.name}" for {user.email}')
                else:
                    self.stdout.write(f'Category "{category.name}" already exists for {user.email}')

        self.stdout.write(self.style.SUCCESS('Default categories created successfully'))
