from django.urls import path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from graphene_django.views import GraphQLView
from .schema import schema

from .views import (
    # Auth
    UserLoginView, UserLogoutView, UserPost, UserProdDetailView,
    # Address
    AddressList,
    # Categories
    LogistCategoryList, ServiceCategoryList, VehicleCategoryList, SparePartCategoryList,
    # Logistika
    LogistMainList, LogistAddList, LogistList, LogistDetail,
    LogistByCategoryList, LogistByAddressList,
    # Hyzmatlar
    ServiceMainList, ServiceAddList, ServiceList, ServiceDetail,
    ServiceByCategoryList, ServiceByAddressList,
    # Ulaglar
    VehicleMainList, VehicleAddList, VehicleList, VehicleDetail,
    VehicleByCategoryList, VehicleByAddressList,
    # Ätiýaçlyk şaýlar
    SparePartMainList, SparePartAddList, SparePartList, SparePartDetail,
    SparePartByCategoryList, SparePartByAddressList,
    # API Root
    ApiRoot
)
from .functions import confirm_sms


# ====================== SWAGGER ======================
schema_view = get_schema_view(
    openapi.Info(
        title="Siziň API",
        default_version='v1',
        description="Logistika, Hyzmatlar, Ulaglar, Ätiýaçlyk şaýlar üçin API",
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
    path('register/', UserPost.as_view(), name='userprod-list'),
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
    path('logistika/by-category/', LogistByCategoryList.as_view(), name='logist-by-category'),
    path('logistika/by-address/', LogistByAddressList.as_view(), name='logist-by-address'),

    # ====================== HYZMATLAR ======================
    path('hyzmatlar/', ServiceMainList.as_view(), name='service-main'),
    path('hyzmatlar/added/', ServiceAddList.as_view(), name='service-added'),
    path('hyzmatlar/create/', ServiceList.as_view(), name='service-create'),
    path('hyzmatlar/<int:pk>/', ServiceDetail.as_view(), name='service-detail'),
    path('hyzmatlar/by-category/', ServiceByCategoryList.as_view(), name='service-by-category'),
    path('hyzmatlar/by-address/', ServiceByAddressList.as_view(), name='service-by-address'),

    # ====================== ULAGLAR ======================
    path('ulaglar/', VehicleMainList.as_view(), name='vehicle-main'),
    path('ulaglar/added/', VehicleAddList.as_view(), name='vehicle-added'),
    path('ulaglar/create/', VehicleList.as_view(), name='vehicle-create'),
    path('ulaglar/<int:pk>/', VehicleDetail.as_view(), name='vehicle-detail'),
    path('ulaglar/by-category/', VehicleByCategoryList.as_view(), name='vehicle-by-category'),
    path('ulaglar/by-address/', VehicleByAddressList.as_view(), name='vehicle-by-address'),

    # ====================== ÄTIÝAÇLYK ŞAÝLARY ======================
    path('atiyaclik-saylar/', SparePartMainList.as_view(), name='sparepart-main'),
    path('atiyaclik-saylar/added/', SparePartAddList.as_view(), name='sparepart-added'),
    path('atiyaclik-saylar/create/', SparePartList.as_view(), name='sparepart-create'),
    path('atiyaclik-saylar/<int:pk>/', SparePartDetail.as_view(), name='sparepart-detail'),
    path('atiyaclik-saylar/by-category/', SparePartByCategoryList.as_view(), name='sparepart-by-category'),
    path('atiyaclik-saylar/by-address/', SparePartByAddressList.as_view(), name='sparepart-by-address'),

    # ====================== SWAGGER & REDOC ======================
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('graphql/', GraphQLView.as_view(graphiql=True, schema=schema), name='graphql'),
    
    path('app/', index, name='index'),
    path('app/login/', web_login, name='web-login'),

    path('app/logistika/', logist_list, name='logist-list'),
    path('app/logistika/<int:pk>/', logist_detail, name='logist-detail'),

    path('app/hyzmatlar/', service_list, name='service-list'),
    path('app/hyzmatlar/<int:pk>/', service_detail, name='service-detail'),

    path('app/ulaglar/', vehicle_list, name='vehicle-list'),
    path('app/ulaglar/<int:pk>/', vehicle_detail, name='vehicle-detail'),

    path('app/atiyaclik-saylar/', sparepart_list, name='sparepart-list'),
    path('app/atiyaclik-saylar/<int:pk>/', sparepart_detail, name='sparepart-detail'),

    path('send-sms/', send_sms_request, name='send-sms'),
    path('confirm-sms/', confirm_sms, name='confirm-sms'),

]