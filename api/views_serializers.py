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


class ProductListView(generics.ListAPIView):
    # filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['checked', 'category', 'address', 'is_client']
    search_fields = ['name']

    extra_filters = []

    def get_queryset(self):
        queryset = super().get_queryset()

        # Common filters
        category = self.request.query_params.get(self.category_param)
        address = self.request.query_params.get(self.address_param)
        author = self.request.query_params.get(self.author_param)

        if category:
            ids = [int(x) for x in category.split(',')]
            queryset = queryset.filter(category__in=ids)

        if address:
            ids = [int(x) for x in address.split(',')]
            queryset = queryset.filter(address__in=ids)

        if author:
            queryset = queryset.filter(author=author)

        # Extra filters: subclass üsti bilen ulanylyp biler
        for filter_name in getattr(self, 'extra_filters', []):
            value = self.request.query_params.get(filter_name)
            if value is not None:
                queryset = self.apply_extra_filter(queryset, filter_name, value)

        return queryset

    def apply_extra_filter(self, queryset, filter_name, value):
        """Subclasses override edip filter logikasyny kesgitläp biler"""
        return queryset

class BaseProductMainList(ProductListView):
    category_param = 'category'
    address_param = 'address'
    author_param = 'author'

    # Extra filters dictionary subclass-da üýtgetmek üçin
    extra_filters = []

    def get_queryset(self):
        queryset = super().get_queryset()

        # Common filters
        category = self.request.query_params.get(self.category_param)
        address = self.request.query_params.get(self.address_param)
        author = self.request.query_params.get(self.author_param)

        if category:
            ids = [int(x) for x in category.split(',')]
            queryset = queryset.filter(category__in=ids)

        if address:
            ids = [int(x) for x in address.split(',')]
            queryset = queryset.filter(address__in=ids)

        if author:
            queryset = queryset.filter(author=author)

        # Extra filters: subclass üsti bilen ulanylyp biler
        for filter_name in getattr(self, 'extra_filters', []):
            value = self.request.query_params.get(filter_name)
            if value is not None:
                queryset = self.apply_extra_filter(queryset, filter_name, value)

        return queryset

    def apply_extra_filter(self, queryset, filter_name, value):
        """Subclasses override edip filter logikasyny kesgitläp biler"""
        return queryset

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
    name = 'top-product'

    def get_queryset(self):
        queryset = super().get_queryset()
        # URL-den checked=True gelýärmi diýip barlaýarys
        checked = self.request.query_params.get('checked')
        if checked == 'True':
            queryset = queryset.filter(checked=True)
        return queryset

class TopProductAddList(ProductListView):
    queryset = TopProduct.objects.all()
    serializer_class = TopProductListSerializer
    name = 'top-product-added'


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

    # 1. extra_filters sanawyny bir gezek we dogry kesgitlemeli
    extra_filters = ['is_client', 'nirden', 'where', 'bring', 'min', 'max', 'search']

    def get_queryset(self):
        # super().get_queryset() adatça checked=True süzgüçlerini özi edýändir
        queryset = super().get_queryset()

        # Common parameters
        category = self.request.query_params.get('category')
        address = self.request.query_params.get('address')
        author = self.request.query_params.get('author')

        if category:
            ids = [int(x) for x in category.split(',')]
            queryset = queryset.filter(category__in=ids)

        if address:
            ids = [int(x) for x in address.split(',')]
            queryset = queryset.filter(address__in=ids)

        if author:
            queryset = queryset.filter(author=author)

        # Extra filters döwri
        for filter_name in self.extra_filters:
            value = self.request.query_params.get(filter_name)
            if value: # Diňe baha bar bolsa süzgüç ulan
                queryset = self.apply_extra_filter(queryset, filter_name, value)

        return queryset

    def apply_extra_filter(self, queryset, filter_name, value):
        if filter_name == 'is_client':
            return queryset.filter(is_client=value.lower() in ['true', '1'])
        elif filter_name == 'nirden':
            return queryset.filter(nirden__icontains=value)
        elif filter_name == 'where':
            return queryset.filter(where__icontains=value)
        elif filter_name == 'bring':
            return queryset.filter(bring=value.lower() in ['true', '1'])
        elif filter_name == 'min':
            return queryset.filter(price__gte=value)
        elif filter_name == 'max':
            return queryset.filter(price__lte=value)
        elif filter_name == 'search':
            # At boýunça tekst gözlegi
            return queryset.filter(name__icontains=value)
            
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

class LogistUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Logist.objects.all()
    serializer_class = LogistListSerializer

    def update(self, request, *args, **kwargs):
        # partial=True bolanda PATCH, bolmasa PUT ýaly işleýär
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # 1. Esasy suraty (img) dolandyrmak
        is_main_deleted = request.data.get('is_main_image_deleted', 'false')
        if is_main_deleted == 'true':
            if instance.img:
                instance.img.delete(save=False)
            instance.img = None # Meýdançany boşadýarys

        # 2. Goşmaça suratlary ID arkaly pozmak
        delete_images_raw = request.data.get('delete_images', None)
        print(request.data);
        if delete_images_raw:
            if isinstance(delete_images_raw, list):
                delete_images_raw = delete_images_raw[0]
            
            try:
                delete_ids = [int(pk) for pk in str(delete_images_raw).split(',') if pk.strip()]
                # LogistImage - köp suratlary saklaýan model
                ImageLogist.objects.filter(id__in=delete_ids, logist=instance).delete()
            except (ValueError, TypeError):
                pass

        # 3. Täze goşmaça suratlary ugradylan bolsa goşmak
        new_images = request.FILES.getlist('images')
        for img_file in new_images:
            ImageLogist.objects.create(logist=instance, img=img_file)

        # 4. Beýleki tekst we san meýdançalaryny täzelemek
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    

class LogistDetail(generics.RetrieveDestroyAPIView):
    queryset = Logist.objects.all()
    serializer_class = LogistDetailSerializer
    name = 'logist-detail'


# ====================== HYZMATLAR ======================
from django.db.models import Q

class ServiceMainList(ProductListView):
    queryset = Service.objects.all()
    serializer_class = ServiceListSerializer
    name = 'service-main'

    def get_queryset(self):
        # Начинаем с базового набора данных
        queryset = super().get_queryset()
        
        # Получаем параметры из URL
        min_price = self.request.query_params.get('min')
        max_price = self.request.query_params.get('max')
        categories = self.request.query_params.get('category')
        addresses = self.request.query_params.get('address')

        # Фильтр по минимальной цене
        if min_price:
            queryset = queryset.filter(price__gte=min_price)

        # Фильтр по максимальной цене
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # Фильтр по категориям (если выбрано несколько, Flutter шлет "1,2,3")
        if categories:
            category_list = categories.split(',')
            queryset = queryset.filter(category_id__in=category_list)

        # Фильтр по адресу
        if addresses:
            address_list = addresses.split(',')
            queryset = queryset.filter(address_id__in=address_list)

        return queryset.distinct() # Используем distinct, чтобы избежать дублей

class ServiceUpdateAPIView(generics.RetrieveUpdateAPIView):
        queryset = Service.objects.all()
        serializer_class = ServiceListSerializer

        def get_serializer(self, *args, **kwargs):
            kwargs['partial'] = True
            return super().get_serializer(*args, **kwargs)

        def update(self, request, *args, **kwargs):
            instance = self.get_object()
            
            # 1. Öçürilmeli suratlaryň ID sanawyny alýarys (Flutter-den "1,2,5" gelýär)
            delete_images_raw = request.data.get('delete_images', None)
            print('Delete:',request.data)
            is_main_deleted = request.data.get('is_main_image_deleted', 'false')
            if is_main_deleted == 'true':
                    # Suraty bazadan pozýarys (null ýa-da boş goýýarys)
                    instance.img.delete(save=False) # Faýlyň özüni papkadan pozar
                    instance.img = "" # Meýdançany boşadar
            # 2. Goşmaça suratlary pozmak (Seniň öňki kodyň)
            delete_images_raw = request.data.get('delete_images', None)
            if delete_images_raw:

                # Eger Flutter-den sanaw (List) gelse: ['1,2,3']
                if isinstance(delete_images_raw, list):
                    delete_images_raw = delete_images_raw[0]
                
                # Indi split edip bileris
                delete_ids = [int(id) for id in str(delete_images_raw).split(',') if id.strip()]
                try:
                    # String-i sanawa öwürýäris: [1, 2, 5]
                    delete_ids = [int(id) for id in delete_images_raw.split(',') if id.strip()]
                    # Şol ID-leri we şu hyzmata degişli suratlary pozýarys
                    ImageService.objects.filter(id__in=delete_ids, service=instance).delete()
                except ValueError:
                    pass

            # 2. Täze ugradylan suratlary goşmak
            new_images = request.FILES.getlist('images')
            for img in new_images:
                ImageService.objects.create(service=instance, img=img)

            # 3. Beýleki meýdançalary täzelemek (Ady, bahasy we ş.m.)
            return super().update(request, *args, **kwargs)

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
        
        # Query parametrlerini alýarys
        current_addr = self.request.query_params.get('current_addr')
        color = self.request.query_params.get('color')
        gearbox = self.request.query_params.get('gearbox')
        fuel_type = self.request.query_params.get('fuel_type')
        
        # Baha we Ýörelen ýoly (min/max aralygy üçin)
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        max_mileage = self.request.query_params.get('max_mileage')
        min_engine = self.request.query_params.get('min_engine')

        # Filterleri ulanmak
        if current_addr:
            queryset = queryset.filter(current_addr__name__icontains=current_addr)
        
        if color:
            queryset = queryset.filter(color__icontains=color)
            
        if gearbox:
            queryset = queryset.filter(gearbox=gearbox) # 'manual' ýa-da 'automatic'
            
        if fuel_type:
            queryset = queryset.filter(fuel_type=fuel_type) # 'gasoline', 'diesel' we ş.m.

        if min_price:
            queryset = queryset.filter(price__gte=min_price)
            
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
            
        if max_mileage:
            queryset = queryset.filter(mileage__lte=max_mileage)

        if min_engine:
            queryset = queryset.filter(engine_volume__gte=min_engine)

        return queryset

class VehicleUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleListSerializer

    def get_serializer(self, *args, **kwargs):
        kwargs['partial'] = True
        return super().get_serializer(*args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # 1. Esasy suraty (img) pozmak
        is_main_deleted = request.data.get('is_main_image_deleted', 'false')
        if is_main_deleted == 'true':
            if instance.img:
                instance.img.delete(save=False)
                instance.img = ""

        # 2. Goşmaça suratlary (Multi-images) pozmak
        delete_images_raw = request.data.get('delete_images', None)
        if delete_images_raw:
            # Flutter käwagt ['1,2'] görnüşinde ugradýar, şony barladyk
            if isinstance(delete_images_raw, list):
                delete_images_raw = delete_images_raw[0]
            
            try:
                # ID-leri sanawa öwürýäris
                delete_ids = [int(id) for id in str(delete_images_raw).split(',') if id.strip()]
                # VehicleImage - siziň multi-image modeliňiz
                # vehicle - ForeignKey meýdançasy
                ImageVehicle.objects.filter(id__in=delete_ids, vehicle=instance).delete()
            except (ValueError, TypeError):
                pass

        # 3. Täze goşmaça suratlar ugradylan bolsa goşmak
        new_images = request.FILES.getlist('images')
        for img_file in new_images:
            ImageVehicle.objects.create(vehicle=instance, img=img_file)

        # 4. Beýleki maglumatlar (adyny, ýylyny we s.m.) täzelemek
        instance.save()
        return super().update(request, *args, **kwargs)
    
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
        
        # Берем ключи 'min' и 'max', как в твоем логе запроса
        min_price = self.request.query_params.get('min')
        max_price = self.request.query_params.get('max')
        category = self.request.query_params.get('category')
        address = self.request.query_params.get('address')

        if min_price:
            queryset = queryset.filter(price__gte=min_price)
            
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        if category:
            queryset = queryset.filter(category_id=category)

        if address:
            queryset = queryset.filter(address_id=address)

        return queryset


class SparePartUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = SparePart.objects.all()
    serializer_class = SparePartListSerializer

    def get_serializer(self, *args, **kwargs):
        kwargs['partial'] = True
        return super().get_serializer(*args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # 1. Esasy suraty (img) pozmak logikasy
        is_main_deleted = request.data.get('is_main_image_deleted', 'false')
        if is_main_deleted == 'true':
            if instance.img:
                instance.img.delete(save=False) # Faýly papkadan pozýar
                instance.img = "" # Bazada boşadýar

        # 2. Goşmaça suratlary (Multi images) pozmak
        delete_images_raw = request.data.get('delete_images', None)
        if delete_images_raw:
            # Eger List bolsa stringe öwürýäris, soňra sanawa
            if isinstance(delete_images_raw, list):
                delete_images_raw = delete_images_raw[0]
            
            try:
                delete_ids = [int(id) for id in str(delete_images_raw).split(',') if id.strip()]
                # ImageSparePart - siziň model adyňyz şeýledir öýdýärin
                ImageSparePart.objects.filter(id__in=delete_ids, sparepart=instance).delete()
            except (ValueError, TypeError):
                pass

        # 3. Täze goşmaça suratlary ugradylan bolsa goşmak
        new_images = request.FILES.getlist('images')
        for img_file in new_images:
            ImageSparePart.objects.create(sparepart=instance, img=img_file)

        # 4. Maglumatlary ýatda saklamak we beýleki meýdançalary täzelemek
        instance.save()
        return super().update(request, *args, **kwargs)


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
