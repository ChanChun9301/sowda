from rest_framework import serializers
from .models import (
    Address, LogistCategory, ServiceCategory, VehicleCategory, SparePartCategory,
    Logist, Service, Vehicle, SparePart, TopProduct, CarouselImage,
    ImageLogist, ImageService, ImageVehicle, ImageSparePart, ImageTopProduct
)

# ====================== BASE SERIALIZERS & UTILS ======================

class BaseURLImageField(serializers.ImageField):
    """Suratlaryň hemişe doly URL (http://...) bilen gaýtmagyny kepillendirýär"""
    def to_representation(self, value):
        if not value:
            return None
        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(value.url)
        return value.url


class ProductImageSerializer(serializers.ModelSerializer):
    """Ähli köp suratly (Multi-image) modeller üçin umumy arassa serializer"""
    url = BaseURLImageField(source='img', read_only=True)

    class Meta:
        model = ImageLogist  # Dinamiki meýdanlar üçin anyk model möhüm däl, diňe field şol bir bolsa boldy
        fields = ('pk', 'url')

    def to_representation(self, instance):
        # Haýsy modeldigine garamazdan 'pk' we 'url' dogry çykaryp berýär
        return {
            'pk': instance.pk,
            'url': BaseURLImageField().to_representation(instance.img)
        }


class CategoryTreeSerializer(serializers.ModelSerializer):
    """Kategoriýa agajy – subcategories nested görnüşinde"""
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = None
        fields = ('pk', 'name', 'parent', 'subcategories')

    def get_subcategories(self, obj):
        children = obj.subcategories.all()
        return self.__class__(children, many=True, context=self.context).data


# ====================== ADDRESS SERIALIZER ======================

class AddressSerializer(serializers.ModelSerializer):
    subaddresses = serializers.SerializerMethodField()

    class Meta:
        model = Address
        fields = ('pk', 'name', 'parent', 'subaddresses')

    def get_subaddresses(self, obj):
        children = obj.subaddresses.all()
        return AddressSerializer(children, many=True, context=self.context).data


# ====================== CATEGORY SERIALIZERS ======================

class LogistCategorySerializer(CategoryTreeSerializer):
    class Meta(CategoryTreeSerializer.Meta):
        model = LogistCategory


class ServiceCategorySerializer(CategoryTreeSerializer):
    class Meta(CategoryTreeSerializer.Meta):
        model = ServiceCategory


class VehicleCategorySerializer(CategoryTreeSerializer):
    class Meta(CategoryTreeSerializer.Meta):
        model = VehicleCategory


class SparePartCategorySerializer(CategoryTreeSerializer):
    class Meta(CategoryTreeSerializer.Meta):
        model = SparePartCategory


# ====================== BASE PRODUCT SERIALIZERS ======================

class BaseProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    address_name = serializers.CharField(source='address.name', read_only=True)
    img = BaseURLImageField(read_only=True)
    thumbnail_url = BaseURLImageField(source='thumbnail', read_only=True)


class BaseProductDetailSerializer(BaseProductListSerializer):
    category_id = serializers.IntegerField(source='category.id', read_only=True)
    address_id = serializers.IntegerField(source='address.id', read_only=True)
    images = serializers.SerializerMethodField()

    def get_images(self, obj):
        images = obj.images.all()
        return ProductImageSerializer(images, many=True, context=self.context).data


# ====================== GENERIC CREATE MIXIN ======================

class BaseProductCreateMixin:
    image_model = None  # subclass-da kesgitlenýär
    fk_name = ''        # foreign key meýdançasynyň ady

    def create_images(self, obj, images_data):
        if not self.image_model or not self.fk_name:
            return
        for img in images_data:
            self.image_model.objects.create(**{self.fk_name: obj, 'img': img})


# ====================== 1. LOGISTIKA ======================

class LogistListSerializer(BaseProductListSerializer):
    class Meta:
        model = Logist
        fields = (
            'pk', 'name', 'text', 'phone', 'price', 'created', 'img', 'checked',
            'category_name', 'address_name', 'where', 'nirden', 'last_date',
            'bring', 'vip', 'latitude', 'longitude', 'thumbnail_url', 'is_client'
        )


class LogistDetailSerializer(BaseProductDetailSerializer):
    class Meta:
        model = Logist
        fields = (
            'pk', 'name', 'category_id', 'category_name', 'address_id', 'address_name', 
            'text', 'phone', 'price', 'created', 'img', 'checked', 'where', 'nirden', 
            'last_date', 'bring', 'vip', 'latitude', 'longitude', 'images', 'thumbnail_url', 'is_client'
        )


class LogistSerializer(serializers.ModelSerializer, BaseProductCreateMixin):
    category = serializers.IntegerField(write_only=True)
    address = serializers.IntegerField(write_only=True)
    images = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)
    img = serializers.ImageField(required=False, allow_null=True)

    image_model = ImageLogist
    fk_name = 'logist'

    class Meta:
        model = Logist
        fields = (
            'pk', 'name', 'author', 'text', 'phone', 'price', 'img', 'created', 'checked',
            'category', 'address', 'where', 'nirden', 'last_date', 'bring', 'vip',
            'latitude', 'longitude', 'images'
        )

    def create(self, validated_data):
        category_id = validated_data.pop('category')
        address_id = validated_data.pop('address')
        images_data = validated_data.pop('images', [])

        category = LogistCategory.objects.get(pk=category_id)
        address = Address.objects.get(pk=address_id)

        logist = Logist.objects.create(category=category, address=address, **validated_data)
        self.create_images(logist, images_data)
        return logist


# ====================== 2. HYZMATLAR ======================

class ServiceListSerializer(BaseProductListSerializer):
    class Meta:
        model = Service
        fields = (
            'pk', 'name', 'text', 'phone', 'price', 'created', 'img', 'checked',
            'category_name', 'address_name', 'thumbnail_url'
        )


class ServiceDetailSerializer(BaseProductDetailSerializer):
    class Meta:
        model = Service
        fields = (
            'pk', 'name', 'category_id', 'category_name', 'address_id', 'address_name', 
            'text', 'phone', 'price', 'created', 'img', 'checked', 'images', 'thumbnail_url'
        )


class ServiceSerializer(serializers.ModelSerializer, BaseProductCreateMixin):
    category = serializers.IntegerField(write_only=True)
    address = serializers.IntegerField(write_only=True)
    images = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)
    img = serializers.ImageField(required=False, allow_null=True)

    image_model = ImageService
    fk_name = 'service'

    class Meta:
        model = Service
        fields = (
            'pk', 'name', 'author', 'text', 'phone', 'price', 'img', 'created', 'checked',
            'category', 'address', 'images'
        )

    def create(self, validated_data):
        category_id = validated_data.pop('category')
        address_id = validated_data.pop('address')
        images_data = validated_data.pop('images', [])

        category = ServiceCategory.objects.get(pk=category_id)
        address = Address.objects.get(pk=address_id)

        service = Service.objects.create(category=category, address=address, **validated_data)
        self.create_images(service, images_data)
        return service


# ====================== 3. ULAGLAR ======================

class VehicleListSerializer(BaseProductListSerializer):
    current_address_name = serializers.CharField(source='current_addr.name', read_only=True)
    text = serializers.CharField(source='description', read_only=True)

    class Meta:
        model = Vehicle
        fields = (
            'pk', 'name', 'year', 'price', 'mileage', 'text', 'fuel_type', 'img', 
            'created', 'checked', 'category_name', 'address_name', 'current_address_name', 'thumbnail_url'
        )


class VehicleDetailSerializer(BaseProductDetailSerializer):
    current_address_name = serializers.CharField(source='current_addr.name', read_only=True)
    gearbox_display = serializers.CharField(source='get_gearbox_display', read_only=True)
    fuel_type_display = serializers.CharField(source='get_fuel_type_display', read_only=True)

    class Meta:
        model = Vehicle
        fields = (
            'pk', 'name', 'category_id', 'category_name', 'address_id', 'address_name', 
            'current_address_name', 'year', 'color', 'engine_volume', 'mileage', 
            'gearbox', 'gearbox_display', 'fuel_type', 'fuel_type_display', 'price', 
            'vin_code', 'description', 'phone', 'created', 'img', 'checked', 
            'latitude', 'longitude', 'images', 'thumbnail_url'
        )


class VehicleSerializer(serializers.ModelSerializer, BaseProductCreateMixin):
    category = serializers.IntegerField(write_only=True)
    address = serializers.IntegerField(write_only=True)
    current_addr = serializers.IntegerField(write_only=True)
    images = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)
    img = serializers.ImageField(required=False, allow_null=True)

    image_model = ImageVehicle
    fk_name = 'vehicle'

    class Meta:
        model = Vehicle
        fields = (
            'pk', 'name', 'year', 'color', 'engine_volume', 'mileage', 'gearbox', 
            'fuel_type', 'price', 'vin_code', 'description', 'author', 'phone', 
            'img', 'created', 'checked', 'category', 'address', 'current_addr', 
            'latitude', 'longitude', 'images'
        )

    def create(self, validated_data):
        category_id = validated_data.pop('category')
        address_id = validated_data.pop('address')
        current_addr_id = validated_data.pop('current_addr')
        images_data = validated_data.pop('images', [])

        category = VehicleCategory.objects.get(pk=category_id)
        address = Address.objects.get(pk=address_id)
        current_addr = Address.objects.get(pk=current_addr_id)

        vehicle = Vehicle.objects.create(
            category=category, address=address, current_addr=current_addr, **validated_data
        )
        self.create_images(vehicle, images_data)
        return vehicle


# ====================== 4. ZAPÇASTLAR ======================

class SparePartListSerializer(BaseProductListSerializer):
    class Meta:
        model = SparePart
        fields = (
            'pk', 'name', 'text', 'phone', 'price', 'created', 'img', 'checked',
            'category_name', 'address_name', 'thumbnail_url', 'compatibility', 
            'part_number', 'year', 'condition'
        )


class SparePartDetailSerializer(BaseProductDetailSerializer):
    class Meta:
        model = SparePart
        fields = (
            'pk', 'name', 'category_id', 'category_name', 'address_id', 'address_name', 
            'text', 'phone', 'price', 'created', 'img', 'checked', 'images', 'thumbnail_url', 
            'compatibility', 'part_number', 'year', 'condition'
        )


class SparePartSerializer(serializers.ModelSerializer, BaseProductCreateMixin):
    category = serializers.IntegerField(write_only=True)
    address = serializers.IntegerField(write_only=True)
    images = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)
    img = serializers.ImageField(required=False, allow_null=True)

    image_model = ImageSparePart
    fk_name = 'sparepart'

    class Meta:
        model = SparePart
        fields = (
            'pk', 'name', 'author', 'text', 'phone', 'price', 'img', 'created', 'checked',
            'category', 'address', 'images', 'compatibility', 'part_number', 'year', 'condition'
        )

    def create(self, validated_data):
        category_id = validated_data.pop('category')
        address_id = validated_data.pop('address')
        images_data = validated_data.pop('images', [])

        category = SparePartCategory.objects.get(pk=category_id)
        address = Address.objects.get(pk=address_id)

        sparepart = SparePart.objects.create(category=category, address=address, **validated_data)
        self.create_images(sparepart, images_data)
        return sparepart


# ====================== TOP PRODUCT ======================

class TopProductListSerializer(BaseProductListSerializer):
    class Meta:
        model = TopProduct
        fields = (
            'pk', 'name', 'text', 'phone', 'price', 'created', 'img', 'checked',
            'category', 'address_name', 'thumbnail_url'
        )


class TopProductDetailSerializer(BaseProductDetailSerializer):
    category_name = serializers.CharField(source='category', read_only=True)

    class Meta:
        model = TopProduct
        fields = (
            'pk', 'name', 'category_name', 'address_id', 'address_name', 'text', 
            'phone', 'price', 'created', 'img', 'checked', 'images', 'thumbnail_url'
        )


class TopProductSerializer(serializers.ModelSerializer, BaseProductCreateMixin):
    address = serializers.IntegerField(write_only=True)
    images = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)
    img = serializers.ImageField(required=False, allow_null=True)

    image_model = ImageTopProduct
    fk_name = 'top_product'

    class Meta:
        model = TopProduct
        fields = (
            'pk', 'name', 'author', 'text', 'phone', 'price', 'img',
            'created', 'checked', 'category', 'address', 'images'
        )

    def create(self, validated_data):
        address_id = validated_data.pop('address')
        images_data = validated_data.pop('images', [])

        address = Address.objects.get(pk=address_id)
        top_product = TopProduct.objects.create(address=address, **validated_data)
        self.create_images(top_product, images_data)
        return top_product


# ====================== CAROUSEL IMAGE ======================

class CarouselImageSerializer(serializers.ModelSerializer):
    img_url = BaseURLImageField(source='img', read_only=True)
    absolute_link = serializers.SerializerMethodField()

    class Meta:
        model = CarouselImage
        fields = ('pk', 'name', 'img_url', 'link', 'is_active', 'order', 'absolute_link')

    def get_absolute_link(self, obj):
        if not obj.link:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(obj.link) if request else obj.link
