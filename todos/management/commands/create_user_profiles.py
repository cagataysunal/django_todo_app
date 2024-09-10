from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from todos.models import Profile


class Command(BaseCommand):
    help = "Creates user profiles for existing users that don't have one"

    def handle(self, *args, **options):
        users = User.objects.all()
        for user in users:
            Profile.objects.get_or_create(user=user)
        self.stdout.write(self.style.SUCCESS("Successfully created user profiles"))
