from rest_framework import generics, filters, status, pagination
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import jwt
from rest_framework_simplejwt.settings import api_settings

from .models import (
    Address, LogistCategory, ServiceCategory, VehicleCategory, SparePartCategory,
    Logist, Service, Vehicle, SparePart,
    ImageLogist, ImageService, ImageVehicle, ImageSparePart,CarouselImage,
    UserProd,TopProduct
)
from .serializers import (
    AddressSerializer,
    LogistCategorySerializer, ServiceCategorySerializer, VehicleCategorySerializer, SparePartCategorySerializer,
    LogistListSerializer, LogistDetailSerializer, LogistSerializer,
    ServiceListSerializer, ServiceDetailSerializer, ServiceSerializer,
    VehicleListSerializer, VehicleDetailSerializer, VehicleSerializer,
    SparePartListSerializer, SparePartDetailSerializer, SparePartSerializer,CarouselImageSerializer,
    TopProductSerializer,TopProductDetailSerializer,TopProductListSerializer,
)


# ====================== PAGINATION ======================
class MyPagination(pagination.PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 1000



# ====================== AUTH VIEWS ======================
# class UserPost(generics.ListCreateAPIView):
#     queryset = UserProd.objects.all()
#     serializer_class = UserSerializer
#     filter_backends = [filters.SearchFilter]
#     search_fields = ['author']
#     name = 'userprod-list'

class CarouselImageList(generics.ListAPIView):
    """Esasy sahypa üçin işjeň karusel suratlary"""
    queryset = CarouselImage.objects.filter(is_active=True).order_by('order', '-created')
    serializer_class = CarouselImageSerializer
    pagination_class = None  # Karusel üçin pagination gerek däl


class CarouselImageDetail(generics.RetrieveAPIView):
    """Aýratyn karusel (admin ýa-da test üçin)"""
    queryset = CarouselImage.objects.all()
    serializer_class = CarouselImageSerializer
    lookup_field = 'pk'

class UserLoginView(APIView):
    def post(self, request):
        author = request.data.get('author')
        phone_model = request.data.get('phone_model')

        print('!!!', request.data)

        if not author or len(author) != 8 or not author.isdigit():
            return Response(
                {'error': 'Telefon belgisi nädogry.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not phone_model:
            return Response(
                {'error': 'Telefon modeli ýok.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = UserProd.objects.filter(author=author).first()

        if user:
            if user.phone_model != phone_model:
                return Response(
                    {'error': 'Bu nomer başga telefonda ulanyldy.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            user = UserProd.objects.create(
                author=author,
                phone_model=phone_model
            )

        return Response({'user': author}, status=status.HTTP_200_OK)



class UserLogoutView(APIView):
    def post(self, request):
        author = request.data.get('author')
        try:
            user = UserProd.objects.get(author=author)
            user.checked = False
            user.save()
            return Response({'success': 'Çykdy'}, status=status.HTTP_200_OK)
        except UserProd.DoesNotExist:
            return Response({'error': 'Ulanyjy tapylmady'}, status=status.HTTP_400_BAD_REQUEST)


class UserProdDetailView(APIView):
    def get(self, request):
        author = request.GET.get('author')

        try:
            user = UserProd.objects.get(author=author)

            if user.author == author and user.checked == True:
                return Response({'token': True})
            return Response({'token': False, 'detail': 'Telefon nomeri gabat gelmedi'})
        except Exception as e:
            return Response({'token': False, 'detail': str(e)})

# ====================== ADDRESS ======================
class AddressList(generics.ListAPIView):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    name = 'address-list'


# ====================== CATEGORY LISTS ======================
class LogistCategoryList(generics.ListAPIView):
    queryset = LogistCategory.objects.all()
    serializer_class = LogistCategorySerializer
    name = 'logistcategory-list'


class ServiceCategoryList(generics.ListAPIView):
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    name = 'servicecategory-list'


class VehicleCategoryList(generics.ListAPIView):
    queryset = VehicleCategory.objects.all()
    serializer_class = VehicleCategorySerializer
    name = 'vehiclecategory-list'


class SparePartCategoryList(generics.ListAPIView):
    queryset = SparePartCategory.objects.all()
    serializer_class = SparePartCategorySerializer
    name = 'sparepartcategory-list'


# ====================== BASE PRODUCT VIEW MIXIN ======================
class ProductListView(generics.ListAPIView):
    pagination_class = MyPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    checked_param = 'checked'

    def get_queryset(self):
        queryset = self.queryset
        checked = self.request.query_params.get(self.checked_param)
        if checked is not None:
            checked = checked.lower() in ['true', '1']
            queryset = queryset.filter(checked=checked)
        return queryset


class ProductCreateListView(generics.ListCreateAPIView):
    pagination_class = MyPagination


# ====================== Top ======================
class TopProductMainList(ProductListView):
    queryset = TopProduct.objects.all()
    serializer_class = TopProductListSerializer
    name = 'top-product-main'

class TopProductAddList(ProductListView):
    queryset = TopProduct.objects.all()
    serializer_class = TopProductListSerializer
    search_fields = ['author']
    name = 'top-product-added'

    def get_queryset(self):
        queryset = super().get_queryset()
        author = self.request.query_params.get('author')
        return queryset.filter(author=author) if author else queryset.none()

class TopProductList(ProductCreateListView):
    queryset = TopProduct.objects.all()
    serializer_class = TopProductSerializer
    name = 'top-product-create'

class TopProductDetail(generics.RetrieveAPIView):
    queryset = TopProduct.objects.all()
    serializer_class = TopProductDetailSerializer
    name = 'top-product-detail'



# ====================== LOGISTIKA ======================
class LogistMainList(ProductListView):
    queryset = Logist.objects.all()
    serializer_class = LogistListSerializer
    name = 'logist-main'

    def get_queryset(self):
        queryset = super().get_queryset()
        is_client=self.request.query_params.get('is_client')
        nirden = self.request.query_params.get('nirden')
        where = self.request.query_params.get('where')
        bring = self.request.query_params.get('bring')
        category = self.request.query_params.get('category')  # "2,5"
        address = self.request.query_params.get('address')    # "5,7"
        if is_client:
            queryset = queryset.filter(is_client=is_client)
        if nirden:
            queryset = queryset.filter(nirden__icontains=nirden)
        if where:
            queryset = queryset.filter(where__icontains=where)
        if bring is not None:
            queryset = queryset.filter(bring=bring.lower() == 'true')
        if category:
            category_ids = [int(x) for x in category.split(',')]
            queryset = queryset.filter(category__in=category_ids)
        if address:
            address_ids = [int(x) for x in address.split(',')]
            queryset = queryset.filter(address__in=address_ids)

        return queryset


class LogistAddList(ProductListView):
    queryset = Logist.objects.all()
    serializer_class = LogistListSerializer
    search_fields = ['author']
    name = 'logist-added'

    def get_queryset(self):
        queryset = super().get_queryset()
        author = self.request.query_params.get('author')
        return queryset.filter(author=author) if author else queryset.none()


class LogistList(ProductCreateListView):
    queryset = Logist.objects.all()
    serializer_class = LogistSerializer
    name = 'logist-create'


class LogistDetail(generics.RetrieveDestroyAPIView):
    queryset = Logist.objects.all()
    serializer_class = LogistDetailSerializer
    name = 'logist-detail'


# ====================== HYZMATLAR ======================
class ServiceMainList(ProductListView):
    queryset = Service.objects.all()
    serializer_class = ServiceListSerializer
    name = 'service-main'

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')  # "2,5"
        address = self.request.query_params.get('address')    # "5,7"

        if category:
            category_ids = [int(x) for x in category.split(',')]
            queryset = queryset.filter(category__in=category_ids)
        if address:
            address_ids = [int(x) for x in address.split(',')]
            queryset = queryset.filter(address__in=address_ids)

        return queryset


class ServiceAddList(ProductListView):
    queryset = Service.objects.all()
    serializer_class = ServiceListSerializer
    search_fields = ['author']
    name = 'service-added'

    def get_queryset(self):
        queryset = super().get_queryset()
        author = self.request.query_params.get('author')
        return queryset.filter(author=author) if author else queryset.none()


class ServiceList(ProductCreateListView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    name = 'service-create'


class ServiceDetail(generics.RetrieveAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceDetailSerializer
    name = 'service-detail'

# ====================== ULAGLAR ======================
class VehicleMainList(ProductListView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleListSerializer
    name = 'vehicle-main'

    def get_queryset(self):
        queryset = super().get_queryset()
        current_addr = self.request.query_params.get('current_addr')
        category = self.request.query_params.get('category')  # "2,5"
        address = self.request.query_params.get('address')    # "5,7"
        
        if current_addr:
            queryset = queryset.filter(current_addr__name__icontains=current_addr)

        if category:
            category_ids = [int(x) for x in category.split(',')]
            queryset = queryset.filter(category__in=category_ids)
        if address:
            address_ids = [int(x) for x in address.split(',')]
            queryset = queryset.filter(address__in=address_ids)
            
        return queryset


class VehicleAddList(ProductListView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleListSerializer
    search_fields = ['author']
    name = 'vehicle-added'

    def get_queryset(self):
        queryset = super().get_queryset()
        author = self.request.query_params.get('author')
        return queryset.filter(author=author) if author else queryset.none()


class VehicleList(ProductCreateListView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    name = 'vehicle-create'


class VehicleDetail(generics.RetrieveDestroyAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleDetailSerializer
    name = 'vehicle-detail'

# ====================== ÄTIÝAÇLYK ŞAÝLARY ======================
class SparePartMainList(ProductListView):
    queryset = SparePart.objects.all()
    serializer_class = SparePartListSerializer
    name = 'sparepart-main'

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')  # "2,5"
        address = self.request.query_params.get('address')    # "5,7"

        if category:
            category_ids = [int(x) for x in category.split(',')]
            queryset = queryset.filter(category__in=category_ids)
        if address:
            address_ids = [int(x) for x in address.split(',')]
            queryset = queryset.filter(address__in=address_ids)

        return queryset


class SparePartAddList(ProductListView):
    queryset = SparePart.objects.all()
    serializer_class = SparePartListSerializer
    search_fields = ['author']
    name = 'sparepart-added'

    def get_queryset(self):
        queryset = super().get_queryset()
        author = self.request.query_params.get('author')
        return queryset.filter(author=author) if author else queryset.none()


class SparePartList(ProductCreateListView):
    queryset = SparePart.objects.all()
    serializer_class = SparePartSerializer
    name = 'sparepart-create'


class SparePartDetail(generics.RetrieveDestroyAPIView):
    queryset = SparePart.objects.all()
    serializer_class = SparePartDetailSerializer
    name = 'sparepart-detail'

# ====================== API ROOT ======================
class ApiRoot(APIView):
    name = 'api-root'

    def get(self, request, *args, **kwargs):
        return Response({
            'auth': {
                'login': reverse('user-login', request=request),
                'logout': reverse('user-logout', request=request),
                # 'register': reverse(UserPost.name, request=request),
            },
            'addresses': reverse(AddressList.name, request=request),
            'categories': {
                'logistika': reverse(LogistCategoryList.name, request=request),
                'hyzmatlar': reverse(ServiceCategoryList.name, request=request),
                'ulaglar': reverse(VehicleCategoryList.name, request=request),
                'ätiýaçlyk_şaýlar': reverse(SparePartCategoryList.name, request=request),
            },
            'logistika': {
                'list': reverse(LogistMainList.name, request=request),
                'added': reverse(LogistAddList.name, request=request),
                'create': reverse(LogistList.name, request=request),
                # 'by_category': reverse(LogistByCategoryList.name, request=request),
                # 'by_address': reverse(LogistByAddressList.name, request=request),
            },
            'hyzmatlar': {
                'list': reverse(ServiceMainList.name, request=request),
                'added': reverse(ServiceAddList.name, request=request),
                'create': reverse(ServiceList.name, request=request),
                # 'by_category': reverse(ServiceByCategoryList.name, request=request),
                # 'by_address': reverse(ServiceByAddressList.name, request=request),
            },
            'ulaglar': {
                'list': reverse(VehicleMainList.name, request=request),
                'added': reverse(VehicleAddList.name, request=request),
                'create': reverse(VehicleList.name, request=request),
                # 'by_category': reverse(VehicleByCategoryList.name, request=request),
                # 'by_address': reverse(VehicleByAddressList.name, request=request),
            },
            'ätiýaçlyk_şaýlar': {
                'list': reverse(SparePartMainList.name, request=request),
                'added': reverse(SparePartAddList.name, request=request),
                'create': reverse(SparePartList.name, request=request),
                # 'by_category': reverse(SparePartByCategoryList.name, request=request),
                # 'by_address': reverse(SparePartByAddressList.name, request=request),
            },
        })
