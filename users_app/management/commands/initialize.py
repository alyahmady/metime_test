import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import Q


# Run this file using "python manage.py initialize" command


class Command(BaseCommand):
    help = "Superuser(admin) creation on first run"

    def handle(self, *args, **options):
        CustomUser = get_user_model()
        admin_email = os.getenv("DJANGO_ADMIN_EMAIL", "admin@example.com")
        admin_password = os.getenv("DJANGO_ADMIN_PASS", "samplepass123")

        if not CustomUser.objects.filter(
            Q(email=admin_email) | Q(is_superuser=True)
        ).exists():
            CustomUser.objects.create_superuser(
                email=admin_email, password=admin_password
            )

        self.stdout.write(self.style.SUCCESS("Successfully created Superadmin User"))
