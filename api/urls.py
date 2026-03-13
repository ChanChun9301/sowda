# urls.py (täzelenen)

from django.urls import path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from .views import *
from .views_serializers import (
    # Auth
    UserLoginView, UserLogoutView, UserProd, UserProdDetailView,
    # Address
    AddressList,
    # Categories
    LogistCategoryList, ServiceCategoryList, VehicleCategoryList, SparePartCategoryList,
    # Logistika
    LogistMainList, LogistAddList, LogistList, LogistDetail,LogistUpdateAPIView,
    # Hyzmatlar
    ServiceMainList, ServiceAddList, ServiceList, ServiceDetail,ServiceUpdateAPIView,
    # Ulaglar
    VehicleMainList, VehicleAddList, VehicleList, VehicleDetail,VehicleUpdateAPIView,
    # Top
    TopProductMainList,TopProductAddList,TopProductList,TopProductDetail,
    # Ätiýaçlyk şaýlar
    SparePartMainList, SparePartAddList, SparePartList, SparePartDetail,SparePartUpdateAPIView,
    # API Root
    ApiRoot,
    # <<< YENI GOŞULAN >>>
    CarouselImageList, CarouselImageDetail  # <--- GOŞULDY
)
from .functions import confirm_sms


# ====================== SWAGGER ======================
schema_view = get_schema_view(
    openapi.Info(
        title="Siziň API",
        default_version='v1',
        description="Logistika, Hyzmatlar, Ulaglar, Ätiýaçlyk şaýlar we Karusel üçin API",
        contact=openapi.Contact(email="support@mysal.com"),
        license=openapi.License(name="MIT"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


# ====================== URL PATTERNS ======================
urlpatterns = [

    # ====================== API ROOT ======================
    path('', ApiRoot.as_view(), name='api-root'),

    # ====================== AUTH ======================
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('logout/', UserLogoutView.as_view(), name='user-logout'),
    path('register/', UserProd, name='userprod-list'),
    path('confirm-sms/', confirm_sms, name='confirm-sms'),
    path('user-check/', UserProdDetailView.as_view(), name='user-check'),

    # ====================== ADDRESS ======================
    path('addresses/', AddressList.as_view(), name='address-list'),

    # ====================== CATEGORIES ======================
    path('categories/logistika/', LogistCategoryList.as_view(), name='logistcategory-list'),
    path('categories/hyzmatlar/', ServiceCategoryList.as_view(), name='servicecategory-list'),
    path('categories/ulaglar/', VehicleCategoryList.as_view(), name='vehiclecategory-list'),
    path('categories/atiyaclik-saylar/', SparePartCategoryList.as_view(), name='sparepartcategory-list'),

    # ====================== LOGISTIKA ======================
    path('logistika/', LogistMainList.as_view(), name='logist-main'),
    path('logistika/added/', LogistAddList.as_view(), name='logist-added'),
    path('logistika/create/', LogistList.as_view(), name='logist-create'),
    path('logistika/<int:pk>/', LogistDetail.as_view(), name='logist-detail'),
    path('logistika/update/<int:pk>/', LogistUpdateAPIView.as_view(), name='logist-update'),

    # ====================== HYZMATLAR ======================
    path('hyzmatlar/', ServiceMainList.as_view(), name='service-main'),
    path('hyzmatlar/added/', ServiceAddList.as_view(), name='service-added'),
    path('hyzmatlar/create/', ServiceList.as_view(), name='service-create'),
    path('hyzmatlar/<int:pk>/', ServiceDetail.as_view(), name='service-detail'),
    path('hyzmatlar/update/<int:pk>/', ServiceUpdateAPIView.as_view(), name='service-update'),

    # ====================== TOP HARYTLAR ======================
    path('top-products/', TopProductMainList.as_view(), name='top-product-main'),
    path('top-products/added/', TopProductAddList.as_view(), name='top-product-added'),
    path('top-products/create/', TopProductList.as_view(), name='top-product-create'),
    path('top-products/<int:pk>/', TopProductDetail.as_view(), name='top-product-detail'),


    # ====================== ULAGLAR ======================
    path('car/', VehicleMainList.as_view(), name='vehicle-main'),
    path('car/added/', VehicleAddList.as_view(), name='vehicle-added'),
    path('car/create/', VehicleList.as_view(), name='vehicle-create'),
    path('car/<int:pk>/', VehicleDetail.as_view(), name='vehicle-detail'),
    path('car/update/<int:pk>/', VehicleUpdateAPIView.as_view(), name='vehicle-update'),

    # ====================== ÄTIÝAÇLYK ŞAÝLARY ======================
    path('spares/', SparePartMainList.as_view(), name='sparepart-main'),
    path('spares/added/', SparePartAddList.as_view(), name='sparepart-added'),
    path('spares/create/', SparePartList.as_view(), name='sparepart-create'),
    path('spares/<int:pk>/', SparePartDetail.as_view(), name='sparepart-detail'),
    path('spares/update/<int:pk>/', SparePartUpdateAPIView.as_view(), name='spare-update'),

    # ====================== CAROUSEL (YENI GOŞULAN) ======================
    path('carousel/', CarouselImageList.as_view(), name='carousel-list'),
    path('carousel/<int:pk>/', CarouselImageDetail.as_view(), name='carousel-detail'),

    # ====================== SWAGGER & REDOC ======================
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # ====================== WEB (Frontend) ======================
    path('app/', index, name='index'),
    path('app/login/', web_login, name='web-login'),

    path('app/logistika/', logist_list, name='logist-list'),
    path('app/logistika/<int:pk>/', logist_detail, name='logist-detail'),

    path('app/hyzmatlar/', service_list, name='service-list'),
    path('app/hyzmatlar/<int:pk>/', service_detail, name='service-detail'),

    path('app/ulaglar/', vehicle_list, name='vehicle-list'),
    path('app/ulaglar/<int:pk>/', vehicle_detail, name='vehicle-detail'),

    path('app/spares/', sparepart_list, name='sparepart-list'),
    path('app/spares/<int:pk>/', sparepart_detail, name='sparepart-detail'),

    path('confirm-sms/', confirm_sms, name='confirm-sms'),

]