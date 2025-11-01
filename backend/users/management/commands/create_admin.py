from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os


class Command(BaseCommand):
    help = (
        "Create or upgrade a superuser from environment variables.\n"
        "Set ADMIN_USERNAME, ADMIN_EMAIL and ADMIN_PASSWORD before running."
    )

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.getenv('ADMIN_USERNAME') or os.getenv('DJANGO_ADMIN_USERNAME') or 'admin'
        email = os.getenv('ADMIN_EMAIL') or os.getenv('DJANGO_ADMIN_EMAIL') or 'admin@example.com'
        password = os.getenv('ADMIN_PASSWORD') or os.getenv('DJANGO_ADMIN_PASSWORD')

        if not password:
            self.stdout.write(self.style.ERROR('ADMIN_PASSWORD environment variable is not set. Aborting.'))
            return

        try:
            user = User.objects.filter(username=username).first()
            if user:
                changed = False
                if not user.is_superuser or not user.is_staff:
                    user.is_superuser = True
                    user.is_staff = True
                    changed = True
                # ensure email and password updated if provided
                if email and user.email != email:
                    user.email = email
                    changed = True
                if changed:
                    user.set_password(password)
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f'Upgraded existing user "{username}" to superuser and updated credentials.'))
                else:
                    # still ensure password is set to provided one
                    user.set_password(password)
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f'Existing user "{username}" already superuser — password updated.'))
                return

            # create new superuser
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Created superuser "{username}"'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to create/upgrade superuser: {e}'))
