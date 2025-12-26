# app/reset_inactive_users.py
import os
import django
from datetime import timedelta
from django.utils import timezone

# Настройка Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sowda.settings")
django.setup()

from app.models import UserProd

def reset_inactive_users():
    one_month_ago = timezone.now() - timedelta(days=30)
    users_updated = UserProd.objects.filter(checked=True, sms_sent_at__lt=one_month_ago).update(checked=False)
    print(f"Updated {users_updated} users")

if __name__ == "__main__":
    reset_inactive_users()


#  0 0 * * * /path/to/venv/bin/python /path/to/manage.py reset_inactive_users
