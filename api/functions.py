from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import *
import bcrypt

@api_view(['POST'])
def send_sms_request(request):
    author = request.data.get('author')
    if not author or len(author) != 8:
        return Response({'error': 'Telefon belgisi nädogry.'}, status=status.HTTP_400_BAD_REQUEST)

    user, created = UserProd.objects.get_or_create(author=author)
    user.sms_sent_at = timezone.now()  # wagt bellenýär
    user.checked = False
    user.save()

    # Bu ýerde SMS ugratmak logikasy goşup bilersiňiz.
    return Response({'success': 'SMS ugradyldy. 10 minutda tassyklamaly.'})

@api_view(['POST'])
def confirm_sms(request):
    author = request.data.get('author')
    try:
        user = UserProd.objects.get(author=author)

        if not user.is_sms_valid():
            return Response({'error': 'SMS wagty gutardy. Täzeden sorap görüň.'}, status=status.HTTP_400_BAD_REQUEST)

        user.checked = True
        user.save()
        return Response({'success': 'SMS tassyklama üstünlikli.'})
    except UserProd.DoesNotExist:
        return Response({'error': 'Ulanyjy tapylmady'}, status=status.HTTP_404_NOT_FOUND)


@receiver(post_save, sender=UserProd)
def user_created(sender, instance, created, **kwargs):
    if created:
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