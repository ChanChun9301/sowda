# app/management/commands/reset_inactive_users.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from app.models import UserProd

class Command(BaseCommand):
    help = "Reset checked=False for inactive users"

    def handle(self, *args, **kwargs):
        one_month_ago = timezone.now() - timedelta(days=30)
        users_updated = UserProd.objects.filter(checked=True, sms_sent_at__lt=one_month_ago).update(checked=False)
        self.stdout.write(f"Updated {users_updated} users")

#  0 0 * * * /path/to/venv/bin/python /path/to/manage.py reset_inactive_users
