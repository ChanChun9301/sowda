import bcrypt
import jwt
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import UserProd


# ====================== SMS TASSYKLAMA ======================
SMS_VALIDITY_MINUTES = 10  # SMS möhleti


def is_sms_valid(user):
    """SMS wagty gutardy ýa ýok"""
    if not user.sms_sent_at:
        return False
    delta = timezone.now() - user.sms_sent_at
    return delta <= timedelta(minutes=SMS_VALIDITY_MINUTES)


@api_view(['POST'])
def send_sms_request(request):
    author = request.data.get('author')
    if not author or len(author) != 8 or not author.isdigit():
        return Response(
            {'error': 'Telefon belgisi nädogry. 8 sanly bolmaly.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user, created = UserProd.objects.get_or_create(author=author)
    user.sms_sent_at = timezone.now()
    user.checked = False
    user.save()

    # BU ÝERDE SMS UGRATMAK LOGIKASY GOŞUP BILERSIŇIZ
    # mysal üçin: send_sms_to_user(author)
    print(f"[SMS] {author} üçin tassyklama kody ugradyldy.")

    return Response({
        'success': f'SMS ugradyldy. {SMS_VALIDITY_MINUTES} minutda tassyklamaly.'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def confirm_sms(request):
    author = request.data.get('author')
    code = request.data.get('code')  # eger kod gerek bolsa

    if not author:
        return Response({'error': 'Telefon belgisi gerek.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = UserProd.objects.get(author=author)

        if not is_sms_valid(user):
            return Response(
                {'error': f'SMS wagty gutardy. Täzeden sorap görüň.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Eger kod bar bolsa, ony barlaň
        # if code != user.sms_code: return error

        user.checked = True
        user.sms_sent_at = None  # wagty arassala
        user.save()

        # JWT token döret
        refresh = settings.SIMPLE_JWT['REFRESH_TOKEN_CLASS'].for_user(user)
        return Response({
            'success': 'SMS tassyklama üstünlikli!',
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user_id': user.id,
            'author': user.author
        }, status=status.HTTP_200_OK)

    except UserProd.DoesNotExist:
        return Response({'error': 'Ulanyjy tapylmady'}, status=status.HTTP_404_NOT_FOUND)


# ====================== HASH & VERIFY ======================
def hash_password(password: str) -> bytes:
    """Paroly hash edýär (bcrypt)"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def verify_password(plain_password: str, hashed_password: bytes) -> bool:
    """Paroly barlaýar"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)



# ====================== USER CREATED SIGNAL ======================
@receiver(post_save, sender=UserProd)
def user_created(sender, instance, created, **kwargs):
    if created:
        print(f"[SIGNAL] Täze ulanyjy döredildi: {instance.author}")


# ====================== TOKEN BARLAG (yardamçy) ======================
def validate_jwt_token(token: str):
    """Tokeni barlaýar we ulanyjy maglumatlaryny gaýtarýar"""
    try:
        payload = jwt.decode(token, settings.SIMPLE_JWT['SIGNING_KEY'], algorithms=["HS256"])
        user_id = payload.get('user_id')
        user = UserProd.objects.get(id=user_id)
        return {'valid': True, 'user': user}
    except (jwt.ExpiredSignatureError, jwt.DecodeError, UserProd.DoesNotExist):
        return {'valid': False, 'error': 'Token nädogry ýa-da möhleti gutardy'}