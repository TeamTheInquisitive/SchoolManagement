from django.core.management.base import BaseCommand
from apps.core.models import School
from apps.accounts.models import User


class Command(BaseCommand):
    help = 'Seed demo school and users'

    def handle(self, *args, **kwargs):
        school, _ = School.objects.get_or_create(
            code='demo',
            defaults={'name': 'Demo School', 'email': 'admin@school.com'}
        )

        users = [
            {'email': 'admin@school.com', 'full_name': 'Admin User', 'role': 'admin'},
            {'email': 'jane@teacher.com', 'full_name': 'Dr. Jane Smith', 'role': 'teacher'},
            {'email': 'john@student.com', 'full_name': 'John Doe', 'role': 'student'},
        ]
        for u in users:
            if not User.objects.filter(email=u['email']).exists():
                User.objects.create_user(
                    email=u['email'], password='password123',
                    full_name=u['full_name'], role=u['role'],
                    school=school, is_email_verified=True
                )
        self.stdout.write(self.style.SUCCESS('Demo data seeded'))
