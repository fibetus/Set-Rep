from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Check users in the database'

    def handle(self, *args, **options):
        users = User.objects.all()
        if users:
            self.stdout.write(self.style.SUCCESS(f'Found {users.count()} users:'))
            for user in users:
                self.stdout.write(f'Username: {user.username}')
                self.stdout.write(f'Email: {user.email}')
                self.stdout.write(f'Is Active: {user.is_active}')
                self.stdout.write(f'Date Joined: {user.date_joined}')
                self.stdout.write('---')
        else:
            self.stdout.write(self.style.WARNING('No users found in the database.')) 