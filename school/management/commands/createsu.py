from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
import os

class Command(BaseCommand):
    help = "Create a superuser and default groups"

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@gmail.com")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "admin123")

        # 🔹 Create superuser if not exists
        user, created = User.objects.get_or_create(username=username, defaults={
            "email": email,
            "is_staff": True,
            "is_superuser": True,
        })
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created"))
        else:
            self.stdout.write(self.style.WARNING(f"Superuser '{username}' already exists"))

        # 🔹 Create groups
        for group_name in ["Admin", "Faculty", "Student"]:
            Group.objects.get_or_create(name=group_name)

        # 🔹 Add superuser to Admin group
        admin_group = Group.objects.get(name="Admin")
        if not user.groups.filter(name="Admin").exists():
            user.groups.add(admin_group)
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' added to Admin group"))

