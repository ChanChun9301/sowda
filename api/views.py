from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import jwt
from rest_framework_simplejwt.settings import api_settings

from .models import (
    Address, LogistCategory, ServiceCategory, VehicleCategory, SparePartCategory,
    Logist, Service, Vehicle, SparePart,
    ImageLogist, ImageService, ImageVehicle, ImageSparePart,
    UserProd, CarouselImage
)


# ====================== WEB VIEWS ======================

def index(request):
    author = request.GET.get('author')
    token = False
    user_id = None

    if author and len(author) >= 8:
        author = author[-8:]
        try:
            user = UserProd.objects.get(author=author)
            token = user.checked
            user_id = user.id
        except UserProd.DoesNotExist:
            token = False

    # Diňe 4 modelden iň soňky 8
    context = {
        'logist': Logist.objects.filter(checked=True)[:8],
        'service': Service.objects.filter(checked=True)[:8],
        'vehicle': Vehicle.objects.filter(checked=True)[:8],
        'sparepart': SparePart.objects.filter(checked=True)[:8],
        'carousel': CarouselImage.objects.all(),
        'token': token,
        'user_id': user_id,
        'author': author,
    }
    return render(request, 'index.html', context)


def web_login(request):
    if request.method == 'POST':
        author = request.POST.get('author')
        if author and len(author) >= 8:
            author = author[-8:]
            user, created = UserProd.objects.get_or_create(author=author)
            if created:
                messages.success(request, 'Ulanyjy döredildi! SMS tassyklama gerek.')
            else:
                messages.info(request, 'SMS tassyklama gerek.')
            return redirect(f'/app/?author={author}')
        else:
            messages.error(request, 'Telefon belgisi nädogry.')
    return render(request, 'auth/login.html')


# ====================== LOGISTIKA ======================
def logist_list(request):
    items = Logist.objects.filter(checked=True)
    context = {'logist': items, 'title': 'Logistika'}
    return render(request, 'logist.html', context)


def logist_detail(request, pk):
    item = get_object_or_404(Logist, pk=pk, checked=True)
    images = ImageLogist.objects.filter(logist=item)
    context = {'logist': item, 'images': images}
    return render(request, 'logist_detail.html', context)


# ====================== HYZMATLAR ======================
def service_list(request):
    items = Service.objects.filter(checked=True)
    context = {'service': items, 'title': 'Hyzmatlar'}
    return render(request, 'service.html', context)


def service_detail(request, pk):
    item = get_object_or_404(Service, pk=pk, checked=True)
    images = ImageService.objects.filter(service=item)
    context = {'service': item, 'images': images}
    return render(request, 'service_detail.html', context)


# ====================== ULAGLAR ======================
def vehicle_list(request):
    items = Vehicle.objects.filter(checked=True)
    context = {'vehicle': items, 'title': 'Ulaglar'}
    return render(request, 'vehicle.html', context)


def vehicle_detail(request, pk):
    item = get_object_or_404(Vehicle, pk=pk, checked=True)
    images = ImageVehicle.objects.filter(vehicle=item)
    context = {'vehicle': item, 'images': images}
    return render(request, 'vehicle_detail.html', context)


# ====================== ÄTIÝAÇLYK ŞAÝLARY ======================
def sparepart_list(request):
    items = SparePart.objects.filter(checked=True)
    context = {'sparepart': items, 'title': 'Ätiýaçlyk şaýlar'}
    return render(request, 'sparepart.html', context)


def sparepart_detail(request, pk):
    item = get_object_or_404(SparePart, pk=pk, checked=True)
    images = ImageSparePart.objects.filter(sparepart=item)
    context = {'sparepart': item, 'images': images}
    return render(request, 'sparepart_detail.html', context)


# ====================== TOKEN BARLAG (API + WEB) ======================
class UserProdDetailView(APIView):
    def get(self, request):
        author = request.GET.get('author')
        token = request.GET.get('token')

        if not author or not token:
            return Response({'token': False, 'detail': 'Maglumat ýeterlik däl'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded = jwt.decode(token, api_settings.SIGNING_KEY, algorithms=["HS256"])
            user_id = decoded.get('user_id')
            user = UserProd.objects.get(id=user_id, author=author)

            return Response({
                'token': user.checked,
                'user_id': user.id,
                'author': user.author
            })
        except (jwt.ExpiredSignatureError, jwt.DecodeError, UserProd.DoesNotExist):
            return Response({'token': False, 'detail': 'Token nädogry ýa-da möhleti gutardy'}, status=status.HTTP_401_UNAUTHORIZED)