import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create the configured Django superuser if it does not exist."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        if not username or not password:
            raise CommandError(
                "Set DJANGO_SUPERUSER_USERNAME and DJANGO_SUPERUSER_PASSWORD."
            )

        user_model = get_user_model()
        user = user_model.objects.filter(username=username).first()
        if user:
            if not user.is_superuser:
                raise CommandError(
                    f"User {username!r} exists but is not a superuser."
                )
            self.stdout.write(f"Superuser {username!r} already exists.")
            return

        user_model.objects.create_superuser(
            username=username,
            email=os.environ.get("DJANGO_SUPERUSER_EMAIL", ""),
            password=password,
        )
        self.stdout.write(self.style.SUCCESS(f"Created superuser {username!r}."))
