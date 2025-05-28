from rest_framework import generics, filters, status, pagination
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.contrib.auth import authenticate
from .models import *
from .serializers import *
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class MyPagination(pagination.PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 1000

@receiver(post_save, sender=UserProd)
def log_userprod_save(sender, instance, created, **kwargs):
    action = "Created" if created else "Updated"
    AuditLog.objects.create(user=instance.author, action=f"UserProd {action}")

@receiver(post_delete, sender=UserProd)
def log_userprod_delete(sender, instance, **kwargs):
    AuditLog.objects.create(user=instance.author, action="UserProd Deleted")

class UserPost(generics.ListCreateAPIView):
    queryset = UserProd.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['author']
    name = 'userprod-list'

class UserLoginView(APIView):
    def post(self, request):
        author = request.data.get('author')
        password = request.data.get('password')

        user = authenticate(username=author, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            user.checked = True
            user.save()
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': user.author
            })
        return Response({'error': 'Nädogry maglumat.'}, status=status.HTTP_401_UNAUTHORIZED)

class UserCreate(APIView):
    name = 'userprod-list'

    def post(self, request):
        data = request.data
        if UserProd.objects.filter(author=data.get('author')).exists():
            return Response({'error': 'Ulanyjy eýýäm bar.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        if UserProd.objects.filter(author=author, checked=True).exists():
            return Response({'token': True})
        return Response({'token': False})

class AddressList(generics.ListAPIView):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    name = 'address-list'

class AddressDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    name = 'address-detail'

#----------------------------
class NewsList(generics.ListAPIView):
    serializer_class = NewsSerializer
    filter_backends = [filters.SearchFilter]
    pagination_class = MyPagination
    search_fields = ['name']
    name = 'news-list'

    def get_queryset(self):
        queryset = News.objects.all()
        checked = self.request.query_params.get('checked')
        if checked is not None:
            checked = checked.lower() in ['true', '1']
            queryset = queryset.filter(checked=checked)
        return queryset

class NewsDetail(generics.RetrieveAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    name = 'news-detail'

class NewsCategoryList(generics.ListAPIView):
    queryset = NewsCategory.objects.all()
    serializer_class = NewsCategorySerializer
    name = 'newscategory-list'

class NewsByCategoryList(generics.ListAPIView):
    serializer_class = NewsSerializer
    filter_backends = [filters.SearchFilter]
    pagination_class = MyPagination
    search_fields = ['category__name']
    name = 'news_by_category-list'

    def get_queryset(self):
        queryset = News.objects.all()
        checked = self.request.query_params.get('checked')
        if checked is not None:
            checked = checked.lower() in ['true', '1']
            queryset = queryset.filter(checked=checked)
        return queryset

#------------------------------------
class ImageList(generics.ListAPIView):
    queryset = ImageTop.objects.all()
    serializer_class = ImageTopSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'top']
    name = 'imagetop-list'

class ImageDetail(generics.RetrieveAPIView):
    queryset = ImageTop.objects.all()
    serializer_class = ImageTopSerializer
    name = 'imagetop-detail'

class CarouselList(generics.ListAPIView):
    queryset = CarouselImage.objects.all()
    serializer_class = CarouselSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'address']
    name = 'carousel-list'

class CarouselDetail(generics.RetrieveAPIView):
    queryset = CarouselImage.objects.all()
    serializer_class = CarouselSerializer
    name = 'carousel-detail'



class TopProductsList(generics.ListAPIView):
    serializer_class = TopProductsSerializer
    filter_backends = [filters.SearchFilter]
    pagination_class = MyPagination
    search_fields = ['name']
    name = 'topmain-list'

    def get_queryset(self):
        queryset = TopProducts.objects.all()
        checked = self.request.query_params.get('checked')
        if checked is not None:
            checked = checked.lower() in ['true', '1']
            queryset = queryset.filter(checked=checked)
        return queryset

class TopProductsDetail(generics.RetrieveAPIView):
    queryset = TopProducts.objects.all()
    serializer_class = TopProductDetailSerializer
    name = 'topmain-detail'




class CarMainList(generics.ListAPIView):
    queryset = Car.objects.all()
    serializer_class = CarListSerializer
    filter_backends = [filters.SearchFilter]
    pagination_class = MyPagination
    search_fields = ['name']
    name = 'carmain-list'

    def get_queryset(self):
        queryset = super().get_queryset()
        checked = self.request.query_params.get('checked')

        if checked is not None:
            checked = bool(checked) 
            queryset = queryset.filter(checked=checked)

        return queryset

class CarAddList(generics.ListAPIView):
    queryset = Car.objects.all()
    serializer_class = CarListSerializer
    filter_backends = [filters.SearchFilter]
    pagination_class = MyPagination
    search_fields = ['author']
    name = 'car-added-list'

    def get_queryset(self):
        queryset = super().get_queryset()
        author = self.request.query_params.get('author')

        if author:
            author = str(author) 
            queryset = queryset.filter(author=author)
        else:
            queryset=[]

        return queryset

class CarList(generics.ListCreateAPIView):
    queryset = Car.objects.all()
    pagination_class = MyPagination
    serializer_class = CarSerializer
    name = 'car-list'

class CarDetail(generics.RetrieveDestroyAPIView):
    queryset = Car.objects.all()
    serializer_class = CarDetailSerializer
    name = 'car-detail'

class CarCategoryList(generics.ListAPIView):
    queryset = CarCategory.objects.all()
    
    serializer_class = CarCategorySerializer
    name = 'carcategory-list'

class CarByCategoryList(generics.ListAPIView):
    category=CarCategorySerializer
    queryset = Car.objects.all()
    serializer_class = CarListSerializer
    filter_backends = [filters.SearchFilter]
    pagination_class = MyPagination
    search_fields = ['category__name']
    name = 'car_by_category-list'

    def get_queryset(self):
        queryset = super().get_queryset()
        checked = self.request.query_params.get('checked')

        if checked is not None:
            checked = bool(checked) 
            queryset = queryset.filter(checked=checked)

        return queryset

class CarByAddressList(generics.ListAPIView):
    address=AddressSerializer
    queryset = Car.objects.all()
    pagination_class = MyPagination
    serializer_class = CarListSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['address__name']
    name = 'car_by_address-list'

    def get_queryset(self):
        queryset = super().get_queryset()
        checked = self.request.query_params.get('checked')

        if checked is not None:
            checked = bool(checked) 
            queryset = queryset.filter(checked=checked)

        return queryset


class ElinMainList(generics.ListAPIView):
    queryset = Elin.objects.all()
    serializer_class = ElinSerializer
    filter_backends = [filters.SearchFilter]
    pagination_class = MyPagination
    search_fields = ['name']
    name = 'elinmain-list'

    def get_queryset(self):
        queryset = super().get_queryset()
        checked = self.request.query_params.get('checked')

        if checked is not None:
            checked = bool(checked) 
            queryset = queryset.filter(checked=checked)

        return queryset

class ElinAddList(generics.ListAPIView):
    queryset = Elin.objects.all()
    serializer_class = ElinListSerializer
    filter_backends = [filters.SearchFilter]
    pagination_class = MyPagination
    search_fields = ['author']
    name = 'elin-added-list'

    def get_queryset(self):
        queryset = super().get_queryset()
        author = self.request.query_params.get('author')

        print(author)
        if author:
            author = str(author) 
            queryset = queryset.filter(author=author)
        else:
            queryset=[]

        return queryset
    
class ElinList(generics.ListCreateAPIView):
    queryset = Elin.objects.all()
    serializer_class = ElinSerializer
    pagination_class = MyPagination
    name = 'elin-list'

class ElinDetail(generics.RetrieveDestroyAPIView):
    queryset = Elin.objects.all()
    serializer_class = ElinDetailSerializer
    name = 'elin-detail'

class ElinCategoryList(generics.ListAPIView):
    queryset = ElinCategory.objects.all()
    serializer_class = ElinCategorySerializer
    name = 'elincategory-list'

class ElinByCategoryList(generics.ListAPIView):
    category=ElinCategorySerializer
    queryset = Elin.objects.all()
    serializer_class = ElinSerializer
    filter_backends = [filters.SearchFilter]
    pagination_class = MyPagination
    search_fields = ['category__name']
    name = 'elin_by_category-list'

    def get_queryset(self):
        queryset = super().get_queryset()
        checked = self.request.query_params.get('checked')

        if checked is not None:
            checked = bool(checked) 
            queryset = queryset.filter(checked=checked)

        return queryset

class ElinByAddressList(generics.ListAPIView):
    address=AddressSerializer
    queryset = Elin.objects.all()
    serializer_class = ElinSerializer
    pagination_class = MyPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['address__name']
    name = 'elin_by_address-list'

    def get_queryset(self):
        queryset = super().get_queryset()
        checked = self.request.query_params.get('checked')

        if checked is not None:
            checked = bool(checked) 
            queryset = queryset.filter(checked=checked)

        return queryset


class LogistMainList(generics.ListAPIView):
    queryset = Logist.objects.all()
    pagination_class = MyPagination
    serializer_class = LogistSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    ordering_fields = ['created']   
    name = 'logistmain-list'

    def get_queryset(self):
        queryset = super().get_queryset()
        checked = self.request.query_params.get('checked')
        nirden = self.request.query_params.get('nirden')
        where = self.request.query_params.get('where')
        bring = self.request.query_params.get('bring')
        category = self.request.query_params.get('category')
        

        if checked is not None:
            checked = bool(checked) 
            queryset = queryset.filter(checked=checked)
        if nirden is not None:
            queryset=queryset.filter(nirden__icontains=nirden)
        if where is not None:
            queryset=queryset.filter(where__icontains=where)
        if category is not None:
            category = int(category)             
            queryset=queryset.filter(category=category)
        if bring is not None:
            queryset=queryset.filter(bring=bring)

        return queryset

class LogistAddList(generics.ListAPIView):
    queryset = Logist.objects.all()
    serializer_class = LogistSerializer
    pagination_class = MyPagination
    search_fields = ['author']
    name = 'logist-added-list'

    def get_queryset(self):
        queryset = super().get_queryset()
        author = self.request.query_params.get('author')

        print(author)
        if author:
            author = str(author) 
            queryset = queryset.filter(author=author)
        else:
            queryset=[]

        return queryset

class LogistList(generics.ListCreateAPIView):
    pagination_class = MyPagination
    queryset = Logist.objects.all()
    serializer_class = LogistSerializer
    name = 'logist-list'

class LogistDetail(generics.RetrieveDestroyAPIView):
    queryset = Logist.objects.all()
    serializer_class = LogistDetailSerializer
    name = 'logist-detail'

class LogistCategoryList(generics.ListAPIView):
    queryset = LogistCategory.objects.all()
    serializer_class = LogistCategorySerializer
    name = 'logistcategory-list'

class LogistByCategoryList(generics.ListAPIView):
    category=LogistCategorySerializer
    queryset = Logist.objects.all()
    pagination_class = MyPagination
    serializer_class = LogistSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['category__name']
    name = 'logist_by_category-list'

    def get_queryset(self):
        queryset = super().get_queryset()
        checked = self.request.query_params.get('checked')

        if checked is not None:
            checked = bool(checked) 
            queryset = queryset.filter(checked=checked)

        return queryset

class LogistByAddressList(generics.ListAPIView):
    address=AddressSerializer
    queryset = Logist.objects.all()
    serializer_class = LogistSerializer
    pagination_class = MyPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['address__name']
    name = 'logist_by_address-list'

    def get_queryset(self):
        queryset = super().get_queryset()
        checked = self.request.query_params.get('checked')

        if checked is not None:
            checked = bool(checked) 
            queryset = queryset.filter(checked=checked)

        return queryset


#------------------------------------
class OtherMainList(generics.ListAPIView):
    queryset = Other.objects.all()
    serializer_class = OtherSerializer
    pagination_class = MyPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    name = 'othermain-list'

    def get_queryset(self):
        queryset = super().get_queryset()
        checked = self.request.query_params.get('checked')

        if checked is not None:
            checked = bool(checked) 
            queryset = queryset.filter(checked=checked)

        return queryset

class OtherAddList(generics.ListAPIView):
    queryset = Other.objects.all()
    serializer_class = OtherListSerializer
    pagination_class = MyPagination
    search_fields = ['author']
    name = 'other-added-list'

    def get_queryset(self):
        queryset = super().get_queryset()
        author = self.request.query_params.get('author')

        if author:
            author = str(author) 
            queryset = queryset.filter(author=author)
        else:
            queryset=[]

        return queryset

class OtherList(generics.ListCreateAPIView):
    queryset = Other.objects.all()
    pagination_class = MyPagination
    serializer_class = OtherSerializer
    name = 'other-list'

class OtherDetail(generics.RetrieveDestroyAPIView):
    queryset = Other.objects.all()
    serializer_class = OtherDetailSerializer
    name = 'other-detail'

class OtherCategoryList(generics.ListAPIView):
    queryset = OtherCategory.objects.all()
    serializer_class = OtherCategorySerializer
    name = 'othercategory-list'

class OtherByCategoryList(generics.ListAPIView):
    category=OtherCategorySerializer
    queryset = Other.objects.all()
    pagination_class = MyPagination
    serializer_class = OtherSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['category__name']
    name = 'other_by_category-list'

    def get_queryset(self):
        queryset = super().get_queryset()
        checked = self.request.query_params.get('checked')

        if checked is not None:
            checked = bool(checked) 
            queryset = queryset.filter(checked=checked)

        return queryset

class OtherByAddressList(generics.ListAPIView):
    address=AddressSerializer
    pagination_class = MyPagination
    queryset = Other.objects.all()
    serializer_class = OtherSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['address__name']
    name = 'other_by_address-list'

    def get_queryset(self):
        queryset = super().get_queryset()
        checked = self.request.query_params.get('checked')

        if checked is not None:
            checked = bool(checked) 
            queryset = queryset.filter(checked=checked)

        return queryset



class ServiceMainList(generics.ListAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    filter_backends = [filters.SearchFilter]
    pagination_class = MyPagination
    search_fields = ['name']
    name = 'servicemain-list'

    def get_queryset(self):
        queryset = super().get_queryset()
        checked = self.request.query_params.get('checked')

        if checked is not None:
            checked = bool(checked) 
            queryset = queryset.filter(checked=checked)

        return queryset

class ServiceAddList(generics.ListAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceListSerializer
    filter_backends = [filters.SearchFilter]
    pagination_class = MyPagination
    search_fields = ['author']
    name = 'service-added-list'

    def get_queryset(self):
        queryset = super().get_queryset()
        author = self.request.query_params.get('author')

        print(author)
        if author:
            author = str(author) 
            queryset = queryset.filter(author=author)
        else:
            queryset=[]

        return queryset

class ServiceList(generics.ListCreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    pagination_class = MyPagination
    name = 'service-list'

class ServiceDetail(generics.RetrieveAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceDetailSerializer
    name = 'service-detail'

class ServiceCategoryList(generics.ListAPIView):
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    name = 'servicecategory-list'

class ServiceByCategoryList(generics.ListAPIView):
    category=ServiceCategorySerializer
    pagination_class = MyPagination
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['category__name']
    name = 'service_by_category-list'

    def get_queryset(self):
        queryset = super().get_queryset()
        checked = self.request.query_params.get('checked')

        if checked is not None:
            checked = bool(checked) 
            queryset = queryset.filter(checked=checked)

        return queryset

class ServiceByAddressList(generics.ListAPIView):
    address=AddressSerializer
    pagination_class = MyPagination
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['address__name']
    name = 'service_by_address-list'

    def get_queryset(self):
        queryset = super().get_queryset()
        checked = self.request.query_params.get('checked')

        if checked is not None:
            checked = bool(checked) 
            queryset = queryset.filter(checked=checked)

        return queryset
#------------

def logist_urls(request):
    return {
        'logist': reverse(LogistMainList.name, request=request),
        'logist-gosulan': reverse(LogistAddList.name, request=request),
        'logist-gosmak': reverse(LogistList.name, request=request),
        'logist - category': reverse(LogistCategoryList.name, request=request),
        'logist - by_category': reverse(LogistByCategoryList.name, request=request),
        'logist - by_address': reverse(LogistByAddressList.name, request=request),
    }

def elin_urls(request):
    return {
        'elin': reverse(ElinMainList.name, request=request),
        'elin-gosulan': reverse(ElinAddList.name, request=request),
        'elin-gosmak': reverse(ElinList.name, request=request),
        'elin - category': reverse(ElinCategoryList.name, request=request),
        'elin - by_category': reverse(ElinByCategoryList.name, request=request),
        'elin - by_address': reverse(ElinByAddressList.name, request=request),
    }

class ApiRoot(APIView):
    name = 'Seýir'
    def get(self, request, *args, **kwargs):
        return Response({
            'auth': {
                'register': reverse(UserCreate.name, request=request),
                'login': reverse('user-login', request=request),
                'logout': reverse('user-logout', request=request),
            },
            'products': {
                'top': reverse(TopProductsList.name, request=request),
                'carousel': reverse(CarouselList.name, request=request),
            },
            'news': {
                'list': reverse(NewsList.name, request=request),
                'categories': reverse(NewsCategoryList.name, request=request),
            },
            'addresses': reverse(AddressList.name, request=request),
        })
