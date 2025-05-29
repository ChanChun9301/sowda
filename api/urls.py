from django.urls import re_path,path
from .views_serializers import *
from .views import *
from .functions import confirm_sms
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('app/',index,name='index'),
    path('app/logist/',logist,name='logist'),
    path('app/logist/<int:pk>/',logist_detail,name='logist'),
    path('app/car/',car,name='car'),
    path('app/car/<int:pk>/',car_detail,name='car'),
    path('app/elin/',elin,name='elin'),
    path('app/elin/<int:pk>/',elin_detail,name='elin'),
    path('app/other/',other_detail,name='other'),
    path('app/other/<int:pk>/',other_detail,name='other'),
    path('app/service/',service,name='service'),
    path('app/service/<int:pk>/',service_detail,name='service'),
    path('app/news/',news,name='news'),
    path('app/news/<int:pk>/',news_detail,name='news'),
    # path('app/logout/',LogoutView.as_view(),name='logout'),
    path('app/login/',webUserCreate, name='login_in'),
    # path('app/login/',UserCreate.as_view(), name='login_in'),

    path('register/', UserCreate.as_view(), name='userprod-list'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('confirm-sms/', confirm_sms, name='confirm-sms'),
    path('logout/', UserLogoutView.as_view(), name='user-logout'),

    re_path(r'^user-logout/$',UserLogoutView.as_view(), name='logout'),
    re_path(r'^userprod-list/$', UserCreate.as_view(), name=UserCreate.name),
    re_path(r'^user-check/$', UserProdDetailView.as_view(), name='login'),

    # re_path(r'^userprod-detail/(?P<pk>[0-9]+)$', UserDetail.as_view(), name=UserDetail.name),
    
    re_path(r'^address-list/$', AddressList.as_view(), name=AddressList.name),
    re_path(r'^address-list/(?P<pk>[0-9]+)$', AddressDetail.as_view(), name=AddressDetail.name),

    re_path(r'^topmain-list/$', TopProductsList.as_view(), name=TopProductsList.name),
    re_path(r'^topmain-list/(?P<pk>[0-9]+)$', TopProductsDetail.as_view(), name=TopProductsDetail.name),
    re_path(r'^imagetop-list/$', ImageList.as_view(), name=ImageList.name),
    re_path(r'^imagetop-list/(?P<pk>[0-9]+)$', ImageDetail.as_view(), name=ImageDetail.name),

    re_path(r'^news-list/$', NewsList.as_view(), name=NewsList.name),
    re_path(r'^news-list/(?P<pk>[0-9]+)$', NewsDetail.as_view(), name=NewsDetail.name),
    re_path(r'^newscategory-list/$', NewsCategoryList.as_view(), name=NewsCategoryList.name),
    re_path(r'^news-by-category-list/$', NewsByCategoryList.as_view(), name=NewsByCategoryList.name),

    re_path(r'^carousel-list/$', CarouselList.as_view(), name=CarouselList.name),
    re_path(r'^carousel-list/(?P<pk>[0-9]+)$', CarouselDetail.as_view(), name=CarouselDetail.name),

    re_path(r'^logist-list/$', LogistList.as_view(), name=LogistList.name),
    re_path(r'^logistmain-list/$', LogistMainList.as_view(), name=LogistMainList.name),
    re_path(r'^logist-added-list/$', LogistAddList.as_view(), name=LogistAddList.name),
    re_path(r'^logist-list/(?P<pk>[0-9]+)$', LogistDetail.as_view(), name=LogistDetail.name),
    re_path(r'^logistcategory-list/$', LogistCategoryList.as_view(), name=LogistCategoryList.name),
    re_path(r'^logist-by-address-list/$', LogistByAddressList.as_view(), name=LogistByAddressList.name),
    re_path(r'^logist-by-category-list/$', LogistByCategoryList.as_view(), name=LogistByCategoryList.name),

    re_path(r'^elin-list/$', ElinList.as_view(), name=ElinList.name),  
    re_path(r'^elinmain-list/$', ElinMainList.as_view(), name=ElinMainList.name),  
    re_path(r'^elin-added-list/$', ElinAddList.as_view(), name=ElinAddList.name),  
    re_path(r'^elin-list/(?P<pk>[0-9]+)$', ElinDetail.as_view(), name=ElinDetail.name),
    re_path(r'^elincategory-list/$', ElinCategoryList.as_view(), name=ElinCategoryList.name),
    re_path(r'^elin-by-address-list/$', ElinByAddressList.as_view(), name=ElinByAddressList.name),
    re_path(r'^elin-by-category-list/$', ElinByCategoryList.as_view(), name=ElinByCategoryList.name),

    re_path(r'^car-list/$', CarList.as_view(), name=CarList.name),
    re_path(r'^carmain-list/$', CarMainList.as_view(), name=CarMainList.name),
    re_path(r'^car-added-list/$', CarAddList.as_view(), name=CarAddList.name),
    re_path(r'^car-list/(?P<pk>[0-9]+)$', CarDetail.as_view(), name=CarDetail.name),
    re_path(r'^carcategory-list/$', CarCategoryList.as_view(), name=CarCategoryList.name),
    re_path(r'^car-by-address-list/$', CarByAddressList.as_view(), name=CarByAddressList.name),
    re_path(r'^car-by-category-list/$', CarByCategoryList.as_view(), name=CarByCategoryList.name),

    re_path(r'^other-list/$', OtherList.as_view(), name=OtherList.name),
    re_path(r'^othermain-list/$', OtherMainList.as_view(), name=OtherMainList.name),
    re_path(r'^other-added-list/$', OtherAddList.as_view(), name=OtherAddList.name),
    re_path(r'^other-list/(?P<pk>[0-9]+)$', OtherDetail.as_view(), name=OtherDetail.name),
    re_path(r'^othercategory-list/$', OtherCategoryList.as_view(), name=OtherCategoryList.name),
    re_path(r'^other-by-address-list/$', OtherByAddressList.as_view(), name=OtherByAddressList.name),
    re_path(r'^other-by-category-list/$', OtherByCategoryList.as_view(), name=OtherByCategoryList.name),

    re_path(r'^service-list/$', ServiceList.as_view(), name=ServiceList.name),
    re_path(r'^servicemain-list/$', ServiceMainList.as_view(), name=ServiceMainList.name),
    re_path(r'^service-added-list/$', ServiceAddList.as_view(), name=ServiceAddList.name),
    re_path(r'^service-list/(?P<pk>[0-9]+)$', ServiceDetail.as_view(), name=ServiceDetail.name),
    re_path(r'^servicecategory-list/$', ServiceCategoryList.as_view(), name=ServiceCategoryList.name),
    re_path(r'^service-by-address-list/$', ServiceByAddressList.as_view(), name=ServiceByAddressList.name),
    re_path(r'^service-by-category-list/$', ServiceByCategoryList.as_view(), name=ServiceByCategoryList.name),

    re_path(r'^$', ApiRoot.as_view(), name=ApiRoot.name)
]








from django.urls import path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Siziň API",
      default_version='v1',
      description="API dokumentasiýasy",
      contact=openapi.Contact(email="email@mysal.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns += [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]