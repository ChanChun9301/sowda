from rest_framework import serializers
from .models import (
    Address, LogistCategory, ServiceCategory, VehicleCategory, SparePartCategory,
    Logist, Service, Vehicle, SparePart, TopProduct, CarouselImage,
    ImageLogist, ImageService, ImageVehicle, ImageSparePart, ImageTopProduct
)


# ====================== BASE SERIALIZERS ======================

class DynamicImageSerializer(serializers.ModelSerializer):
    """Umumy image serializer – URL-ni awtomatik gurýar"""
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        request = self.context.get('request')
        if obj.img and hasattr(obj.img, 'url'):
            url = obj.img.url
            return request.build_absolute_uri(url) if request else url
        return None


class CategoryTreeSerializer(serializers.ModelSerializer):
    """Kategoriýa agajy – subcategories bilen"""
    subcategories = serializers.SerializerMethodField()

    def get_subcategories(self, obj):
        children = obj.subcategories.all()
        return self.__class__(children, many=True, context=self.context).data

    class Meta:
        fields = ('pk', 'name', 'parent', 'subcategories')


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
        fields = ('pk', 'name', 'subcategories')


class ServiceCategorySerializer(CategoryTreeSerializer):
    class Meta(CategoryTreeSerializer.Meta):
        model = ServiceCategory
        fields = ('pk', 'name', 'subcategories')


class VehicleCategorySerializer(CategoryTreeSerializer):
    class Meta(CategoryTreeSerializer.Meta):
        model = VehicleCategory
        fields = ('pk', 'name', 'subcategories')


class SparePartCategorySerializer(CategoryTreeSerializer):
    class Meta(CategoryTreeSerializer.Meta):
        model = SparePartCategory
        fields = ('pk', 'name', 'subcategories')


# ====================== BASE PRODUCT SERIALIZERS ======================

class BaseProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    address_name = serializers.CharField(source='address.name', read_only=True)
    thumbnail_url = serializers.SerializerMethodField()

    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.thumbnail and hasattr(obj.thumbnail, 'url'):
            url = obj.thumbnail.url
            return request.build_absolute_uri(url) if request else url
        return None


class BaseProductDetailSerializer(BaseProductListSerializer):
    images = serializers.SerializerMethodField()

    def get_images(self, obj):
        # Image serializer map
        image_serializer_map = {
            Logist: ImageLogistSerializer,
            Service: ImageServiceSerializer,
            Vehicle: ImageVehicleSerializer,
            SparePart: ImageSparePartSerializer,
            TopProduct: ImageTopProductSerializer,
        }
        serializer_class = image_serializer_map.get(obj.__class__, DynamicImageSerializer)
        images = getattr(obj, 'images', obj.images.all())  # relation fallback
        return serializer_class(images, many=True, context=self.context).data


# ====================== IMAGE SERIALIZERS ======================

class ImageLogistSerializer(DynamicImageSerializer):
    class Meta:
        model = ImageLogist
        fields = ('url',)


class ImageServiceSerializer(DynamicImageSerializer):
    class Meta:
        model = ImageService
        fields = ('url',)


class ImageVehicleSerializer(DynamicImageSerializer):
    class Meta:
        model = ImageVehicle
        fields = ('url',)


class ImageSparePartSerializer(DynamicImageSerializer):
    class Meta:
        model = ImageSparePart
        fields = ('url',)


class ImageTopProductSerializer(DynamicImageSerializer):
    class Meta:
        model = ImageTopProduct
        fields = ('url',)


# ====================== GENERIC CREATE MIXIN ======================

class BaseProductCreateMixin:
    image_model = None  # subclass-da kesgitlensin
    fk_name = ''        # relation field name (Logist, Service, Vehicle...)

    def create_images(self, obj, images_data):
        if not self.image_model or not self.fk_name:
            return
        for img in images_data:
            self.image_model.objects.create(**{self.fk_name: obj, 'img': img})


# ====================== LOGISTIKA ======================

class LogistListSerializer(BaseProductListSerializer):
    class Meta:
        model = Logist
        fields = (
            'pk', 'name', 'text', 'phone', 'price', 'created', 'img', 'checked',
            'category_name', 'address_name', 'where', 'nirden', 'last_date',
            'bring', 'vip', 'latitude', 'longitude', 'thumbnail_url'
        )


class LogistDetailSerializer(BaseProductDetailSerializer):
    class Meta:
        model = Logist
        fields = (
            'pk', 'name', 'address_name', 'text', 'category_name', 'phone', 'price',
            'created', 'img', 'checked', 'where', 'nirden', 'last_date', 'bring',
            'vip', 'latitude', 'longitude', 'images', 'thumbnail_url'
        )


class LogistSerializer(serializers.ModelSerializer, BaseProductCreateMixin):
    category = serializers.IntegerField(write_only=True)
    address = serializers.IntegerField(write_only=True)
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)

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

        logist = Logist.objects.create(
            category=category, address=address, **validated_data
        )

        self.create_images(logist, images_data)
        return logist


# ====================== SERVICE ======================

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
            'pk', 'name', 'address_name', 'text', 'category_name', 'phone', 'price',
            'created', 'img', 'checked', 'images', 'thumbnail_url'
        )


class ServiceSerializer(serializers.ModelSerializer, BaseProductCreateMixin):
    category = serializers.IntegerField(write_only=True)
    address = serializers.IntegerField(write_only=True)
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

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

        service = Service.objects.create(
            category=category, address=address, **validated_data
        )
        self.create_images(service, images_data)
        return service


# ====================== VEHICLE ======================

class VehicleListSerializer(BaseProductListSerializer):
    current_address_name = serializers.CharField(source='current_addr.name', read_only=True)

    class Meta:
        model = Vehicle
        fields = (
            'pk', 'name', 'text', 'phone', 'price', 'created', 'img', 'checked',
            'category_name', 'address_name', 'current_address_name',
            'latitude', 'longitude', 'thumbnail_url'
        )


class VehicleDetailSerializer(BaseProductDetailSerializer):
    current_address_name = serializers.CharField(source='current_addr.name', read_only=True)

    class Meta:
        model = Vehicle
        fields = (
            'pk', 'name', 'address_name', 'text', 'category_name', 'phone', 'price',
            'created', 'img', 'checked', 'current_address_name',
            'latitude', 'longitude', 'images', 'thumbnail_url'
        )


class VehicleSerializer(serializers.ModelSerializer, BaseProductCreateMixin):
    category = serializers.IntegerField(write_only=True)
    address = serializers.IntegerField(write_only=True)
    current_addr = serializers.IntegerField(write_only=True)
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)

    image_model = ImageVehicle
    fk_name = 'vehicle'

    class Meta:
        model = Vehicle
        fields = (
            'pk', 'name', 'author', 'text', 'phone', 'price', 'img', 'created', 'checked',
            'category', 'address', 'current_addr', 'latitude', 'longitude', 'images'
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


# ====================== SPARE PART ======================

class SparePartListSerializer(BaseProductListSerializer):
    class Meta:
        model = SparePart
        fields = (
            'pk', 'name', 'text', 'phone', 'price', 'created', 'img', 'checked',
            'category_name', 'address_name', 'thumbnail_url'
        )


class SparePartDetailSerializer(BaseProductDetailSerializer):
    class Meta:
        model = SparePart
        fields = (
            'pk', 'name', 'address_name', 'text', 'category_name', 'phone', 'price',
            'created', 'img', 'checked', 'images', 'thumbnail_url'
        )


class SparePartSerializer(serializers.ModelSerializer, BaseProductCreateMixin):
    category = serializers.IntegerField(write_only=True)
    address = serializers.IntegerField(write_only=True)
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    image_model = ImageSparePart
    fk_name = 'sparepart'

    class Meta:
        model = SparePart
        fields = (
            'pk', 'name', 'author', 'text', 'phone', 'price', 'img', 'created', 'checked',
            'category', 'address', 'images'
        )

    def create(self, validated_data):
        category_id = validated_data.pop('category')
        address_id = validated_data.pop('address')
        images_data = validated_data.pop('images', [])

        category = SparePartCategory.objects.get(pk=category_id)
        address = Address.objects.get(pk=address_id)

        sparepart = SparePart.objects.create(
            category=category, address=address, **validated_data
        )
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
    images = ImageTopProductSerializer(many=True, read_only=True)

    class Meta:
        model = TopProduct
        fields = (
            'pk', 'name', 'address_name', 'text', 'category', 'phone', 'price',
            'created', 'img', 'checked', 'images', 'thumbnail_url'
        )


class TopProductSerializer(serializers.ModelSerializer, BaseProductCreateMixin):
    address = serializers.IntegerField(write_only=True)
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

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

        top_product = TopProduct.objects.create(
            address=address,
            **validated_data
        )
        self.create_images(top_product, images_data)
        return top_product


# ====================== CAROUSEL IMAGE ======================

class CarouselImageSerializer(serializers.ModelSerializer):
    img_url = serializers.SerializerMethodField()
    absolute_link = serializers.SerializerMethodField()

    class Meta:
        model = CarouselImage
        fields = ('pk', 'name', 'img_url', 'link', 'is_active', 'order', 'absolute_link')

    def get_img_url(self, obj):
        request = self.context.get('request')
        if obj.img and hasattr(obj.img, 'url'):
            return request.build_absolute_uri(obj.img.url) if request else obj.img.url
        return None

    def get_absolute_link(self, obj):
        request = self.context.get('request')
        if obj.link:
            return request.build_absolute_uri(obj.link) if request else obj.link
        return None
