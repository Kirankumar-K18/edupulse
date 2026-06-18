"""
Management command to create the single admin account.
Usage: python manage.py create_admin --email admin@college.edu
"""

from django.core.management.base import BaseCommand
from apps.accounts.models import User

class Command(BaseCommand):
    help = "Create default admin if it does not exist"

    def handle(self, *args, **kwargs):
        email = "smartlecturerreview18@gmail.com"

        if User.objects.filter(email=email).exists():
            self.stdout.write("Admin already exists")
            return

        User.objects.create_superuser(
            email=email,
            password="Smart@12345",
            full_name="System Administrator",
        )

        self.stdout.write(self.style.SUCCESS("Admin created"))