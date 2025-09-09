from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
import os

class Command(BaseCommand):
    help = "Force create a fresh superuser and default groups"

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "admin123")

        # 🔹 Always delete old account with same username
        User.objects.filter(username=username).delete()

        # 🔹 Create new superuser with password
        user = User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created with password '{password}'"))

        # 🔹 Ensure default groups exist
        for group_name in ["Admin", "Faculty", "Student"]:
            Group.objects.get_or_create(name=group_name)

        # 🔹 Add superuser to Admin group
        admin_group = Group.objects.get(name="Admin")
        user.groups.add(admin_group)
        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' added to Admin group"))
