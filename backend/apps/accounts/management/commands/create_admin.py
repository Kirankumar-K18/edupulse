"""
Management command to create the single admin account.
Usage: python manage.py create_admin --email admin@college.edu
"""

import getpass
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from apps.accounts.models import User


class Command(BaseCommand):
    help = 'Create the single admin (superuser) account for Smart Lecturer System'

    def add_arguments(self, parser):
        parser.add_argument('--email',    type=str, help='Admin email (@college.edu)')
        parser.add_argument('--fullname', type=str, default='System Administrator')
        parser.add_argument('--password', type=str, help='Admin password (prompted if omitted)')
        parser.add_argument('--force',    action='store_true', help='Delete existing admin first')

    def handle(self, *args, **options):
        domain = getattr(settings, 'COLLEGE_EMAIL_DOMAIN', 'college.edu')

        # Check existing admin
        existing = User.objects.filter(role=User.Role.ADMIN).first()
        if existing:
            if options['force']:
                existing.delete()
                self.stdout.write(self.style.WARNING(f"Existing admin {existing.email} deleted."))
            else:
                raise CommandError(
                    f"Admin already exists: {existing.email}\n"
                    "Use --force to replace it."
                )

        # Get email
        email = options.get('email')
        if not email:
            email = input(f"Admin email [@{domain}]: ").strip()
        if not email.endswith(f'@{domain}'):
            raise CommandError(f"Email must end with @{domain}")

        # Get password
        password = options.get('password')
        if not password:
            while True:
                password = getpass.getpass("Password (min 8 chars, upper+lower+digit+special): ")
                if len(password) < 8:
                    self.stdout.write(self.style.ERROR("Too short. Try again."))
                    continue
                confirm = getpass.getpass("Confirm password: ")
                if password != confirm:
                    self.stdout.write(self.style.ERROR("Passwords don't match. Try again."))
                    continue
                break

        full_name = options.get('fullname', 'System Administrator')

        try:
            user = User.objects.create_superuser(
                email=email,
                password=password,
                full_name=full_name,
            )
            self.stdout.write(self.style.SUCCESS(
                f"\n✓ Admin account created successfully!\n"
                f"  Email:    {user.email}\n"
                f"  Name:     {user.full_name}\n"
                f"  Role:     {user.role}\n\n"
                f"Login at: /accounts/login/"
            ))
        except Exception as e:
            raise CommandError(f"Failed to create admin: {e}")
