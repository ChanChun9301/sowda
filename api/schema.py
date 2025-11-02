import graphene
from graphene_django import DjangoObjectType
from django.utils import timezone
from datetime import timedelta

from .models import (
    Logist, Service, Vehicle, SparePart,
    LogistCategory, ServiceCategory, VehicleCategory, SparePartCategory,
    ImageLogist, ImageService, ImageVehicle, ImageSparePart,
    Address, UserProd
)


# ====================== IMAGE TYPE (umumy) ======================
class ImageType(DjangoObjectType):
    url = graphene.String()

    class Meta:
        model = None  # Dinamiki model
        fields = ('img',)

    def resolve_url(self, info):
        if self.img:
            return info.context.build_absolute_uri(self.img.url)
        return None


# ====================== ADDRESS ======================
class AddressType(DjangoObjectType):
    class Meta:
        model = Address
        fields = ('id', 'name', 'parent')


# ====================== CATEGORY ======================
class CategoryType(DjangoObjectType):
    class Meta:
        fields = ('id', 'name', 'parent')


# ====================== BASE PRODUCT TYPE ======================
class BaseProductType(graphene.Interface):
    id = graphene.ID()
    name = graphene.String()
    text = graphene.String()
    price = graphene.Decimal()
    phone = graphene.String()
    author = graphene.String()
    created = graphene.DateTime()
    checked = graphene.Boolean()
    address = graphene.Field(AddressType)
    category = graphene.Field(CategoryType)
    images = graphene.List(ImageType)
    thumbnail_url = graphene.String()

    def resolve_thumbnail_url(self, info):
        if self.thumbnail:
            return info.context.build_absolute_uri(self.thumbnail.url)
        return None

    def resolve_images(self, info):
        # Dinamiki surat modeli
        image_map = {
            Logist: ImageLogist,
            Service: ImageService,
            Vehicle: ImageVehicle,
            SparePart: ImageSparePart,
        }
        ImageModel = image_map.get(type(self))
        if ImageModel:
            images = ImageModel.objects.filter(**{f"{self.__class__.__name__.lower()}": self})
            return [ImageType(img=image.img) for image in images]
        return []


# ====================== LOGISTIKA ======================
class LogistType(DjangoObjectType):
    where = graphene.String()
    nirden = graphene.String()
    last_date = graphene.Date()
    bring = graphene.Boolean()
    vip = graphene.Boolean()
    latitude = graphene.Float()
    longitude = graphene.Float()

    class Meta:
        model = Logist
        fields = (
            'id', 'name', 'text', 'price', 'phone', 'author', 'created', 'checked',
            'address', 'category', 'where', 'nirden', 'last_date', 'bring', 'vip',
            'latitude', 'longitude'
        )
        interfaces = (BaseProductType,)


# ====================== HYZMATLAR ======================
class ServiceType(DjangoObjectType):
    class Meta:
        model = Service
        fields = ('id', 'name', 'text', 'price', 'phone', 'author', 'created', 'checked', 'address', 'category')
        interfaces = (BaseProductType,)


# ====================== ULAGLAR ======================
class VehicleType(DjangoObjectType):
    current_addr = graphene.Field(AddressType)
    latitude = graphene.Float()
    longitude = graphene.Float()

    class Meta:
        model = Vehicle
        fields = (
            'id', 'name', 'text', 'price', 'phone', 'author', 'created', 'checked',
            'address', 'category', 'current_addr', 'latitude', 'longitude'
        )
        interfaces = (BaseProductType,)


# ====================== ÄTIÝAÇLYK ŞAÝLARY ======================
class SparePartType(DjangoObjectType):
    part_number = graphene.String()
    brand = graphene.String()
    model = graphene.String()
    year = graphene.Int()
    condition = graphene.String()
    compatibility = graphene.String()

    class Meta:
        model = SparePart
        fields = (
            'id', 'name', 'text', 'price', 'phone', 'author', 'created', 'checked',
            'address', 'category', 'part_number', 'brand', 'model', 'year',
            'condition', 'compatibility'
        )
        interfaces = (BaseProductType,)


# ====================== QUERY ======================
class Query(graphene.ObjectType):
    # Logistika
    logistika = graphene.List(LogistType, checked=graphene.Boolean(), category=graphene.Int())
    logistika_by_id = graphene.Field(LogistType, id=graphene.ID(required=True))

    # Hyzmatlar
    hyzmatlar = graphene.List(ServiceType, checked=graphene.Boolean(), category=graphene.Int())
    hyzmat_by_id = graphene.Field(ServiceType, id=graphene.ID(required=True))

    # Ulaglar
    ulaglar = graphene.List(VehicleType, checked=graphene.Boolean(), category=graphene.Int())
    ulag_by_id = graphene.Field(VehicleType, id=graphene.ID(required=True))

    # Ätiýaçlyk şaýlar
    atiyaclik_saylar = graphene.List(SparePartType, checked=graphene.Boolean(), category=graphene.Int())
    atiyaclik_say_by_id = graphene.Field(SparePartType, id=graphene.ID(required=True))

    # Kategoriýalar
    logistika_categories = graphene.List(CategoryType)
    hyzmat_categories = graphene.List(CategoryType)
    ulag_categories = graphene.List(CategoryType)
    atiyaclik_say_categories = graphene.List(CategoryType)

    # Address
    addresses = graphene.List(AddressType)

    # User
    me = graphene.Field(graphene.types.Scalar)

    # ====================== RESOLVERS ======================
    def resolve_logistika(self, info, checked=None, category=None):
        qs = Logist.objects.filter(checked=True)
        if checked is not None:
            qs = qs.filter(checked=checked)
        if category:
            qs = qs.filter(category_id=category)
        return qs

    def resolve_logistika_by_id(self, info, id):
        return Logist.objects.get(pk=id, checked=True)

    def resolve_hyzmatlar(self, info, checked=None, category=None):
        qs = Service.objects.filter(checked=True)
        if checked is not None: qs = qs.filter(checked=checked)
        if category: qs = qs.filter(category_id=category)
        return qs

    def resolve_hyzmat_by_id(self, info, id):
        return Service.objects.get(pk=id, checked=True)

    def resolve_ulaglar(self, info, checked=None, category=None):
        qs = Vehicle.objects.filter(checked=True)
        if checked is not None: qs = qs.filter(checked=checked)
        if category: qs = qs.filter(category_id=category)
        return qs

    def resolve_ulag_by_id(self, info, id):
        return Vehicle.objects.get(pk=id, checked=True)

    def resolve_atiyaclik_saylar(self, info, checked=None, category=None):
        qs = SparePart.objects.filter(checked=True)
        if checked is not None: qs = qs.filter(checked=checked)
        if category: qs = qs.filter(category_id=category)
        return qs

    def resolve_atiyaclik_say_by_id(self, info, id):
        return SparePart.objects.get(pk=id, checked=True)

    def resolve_logistika_categories(self, info):
        return LogistCategory.objects.all()

    def resolve_hyzmat_categories(self, info):
        return ServiceCategory.objects.all()

    def resolve_ulag_categories(self, info):
        return VehicleCategory.objects.all()

    def resolve_atiyaclik_say_categories(self, info):
        return SparePartCategory.objects.all()

    def resolve_addresses(self, info):
        return Address.objects.all()

    def resolve_me(self, info):
        user = info.context.user
        if user.is_authenticated:
            return {"id": user.id, "author": user.author}
        return None


# ====================== SCHEMA ======================
schema = graphene.Schema(query=Query)