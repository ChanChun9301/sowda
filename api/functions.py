from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *
import bcrypt

@receiver(post_save, sender=UserProd)
def user_created(sender, instance, created, **kwargs):
    if created:
        # Perform any actions you want to take when a new product is created
        print(f"Täze ulanyjy: {instance.author}")

def hash_password(password):
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    
    return hashed_password

def verify_password(plain_password, hashed_password):
    # Convert the plain password to bytes
    plain_password_bytes = plain_password.encode('utf-8')
    
    # Check if the hashed password matches the plain password
    return bcrypt.checkpw(plain_password_bytes, hashed_password)

from django.core.mail import send_mail
from django.dispatch import receiver
from django.db.models.signals import post_save


@receiver(post_save, sender=UserProd)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        send_mail(
            'Hoş geldiňiz!',
            f'Hormatly {instance.author}, siziň ulanyjy hasabyňyz üstünlikli döredildi.',
            'from@example.com',
            [f'{instance.author}@mysal.com'],
            fail_silently=False,
        )

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import UserProd, AuditLog

@receiver(post_save, sender=UserProd)
def log_userprod_save(sender, instance, created, **kwargs):
    action = "Created" if created else "Updated"
    AuditLog.objects.create(user=instance.author, action=f"UserProd {action}")

@receiver(post_delete, sender=UserProd)
def log_userprod_delete(sender, instance, **kwargs):
    AuditLog.objects.create(user=instance.author, action="UserProd Deleted")