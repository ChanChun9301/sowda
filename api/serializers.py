from rest_framework import serializers
from .models import (
    Address, LogistCategory, ServiceCategory, VehicleCategory, SparePartCategory,
    Logist, Service, Vehicle, SparePart,
    ImageLogist, ImageService, ImageVehicle, ImageSparePart
)


# ====================== BASE SERIALIZERS ======================

class DynamicImageSerializer(serializers.ModelSerializer):
    """Umumy surat serializer – URL-ni build edýär"""
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        request = self.context.get('request')
        if obj.img and hasattr(obj.img, 'url'):
            url = obj.img.url
            return request.build_absolute_uri(url) if request else url
        return None


class CategoryTreeSerializer(serializers.ModelSerializer):
    """Kategoriýa agajy – subkategoriýalar bilen"""
    subcategories = serializers.SerializerMethodField()

    def get_subcategories(self, obj):
        children = obj.subcategories.all()
        return self.__class__(children, many=True, context=self.context).data

    class Meta:
        fields = ('pk', 'name', 'parent', 'subcategories')


# ====================== ADDRESS ======================

class AddressSerializer(serializers.ModelSerializer):
    subaddresses = serializers.SerializerMethodField()

    class Meta:
        model = Address
        fields = ('pk', 'name', 'parent', 'subaddresses')

    def get_subaddresses(self, obj):
        children = obj.subaddresses.all()
        return AddressSerializer(children, many=True, context=self.context).data


# ====================== KATEGORIÝALAR ======================

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


# ====================== SURAT SERIALIZERLARY ======================

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


# ====================== PRODUCT BASE (DRY) ======================

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


class BaseProductDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    address_name = serializers.CharField(source='address.name', read_only=True)
    images = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    def get_images(self, obj):
        # Dinamiki surat serializer saýlaýjy
        image_serializer_map = {
            Logist: ImageLogistSerializer,
            Service: ImageServiceSerializer,
            Vehicle: ImageVehicleSerializer,
            SparePart: ImageSparePartSerializer,
        }
        ImageModel = obj.__class__.__name__ + 'Image'
        serializer_class = image_serializer_map.get(obj.__class__, ImageLogistSerializer)
        images = obj.images.all()
        return serializer_class(images, many=True, context=self.context).data

    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.thumbnail:
            url = obj.thumbnail.url
            return request.build_absolute_uri(url) if request else url
        return None


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


class LogistSerializer(serializers.ModelSerializer):
    category = serializers.IntegerField(write_only=True)
    address = serializers.IntegerField(write_only=True)
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)

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

        for img in images_data:
            ImageLogist.objects.create(logist=logist, img=img)

        return logist


# ====================== HYZMATLAR ======================

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


class ServiceSerializer(serializers.ModelSerializer):
    category = serializers.IntegerField(write_only=True)
    address = serializers.IntegerField(write_only=True)
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

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

        for img in images_data:
            ImageService.objects.create(service=service, img=img)

        return service


# ====================== ULAGLAR ======================

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


class VehicleSerializer(serializers.ModelSerializer):
    category = serializers.IntegerField(write_only=True)
    address = serializers.IntegerField(write_only=True)
    current_addr = serializers.IntegerField(write_only=True)
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)

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

        for img in images_data:
            ImageVehicle.objects.create(vehicle=vehicle, img=img)

        return vehicle


# ====================== ÄTIÝAÇLYK ŞAÝLARY ======================

class SparePartListSerializer(BaseProductListSerializer):
    part_number = serializers.CharField(read_only=True)
    brand = serializers.CharField(read_only=True)
    model = serializers.CharField(read_only=True)
    condition = serializers.CharField(read_only=True)

    class Meta:
        model = SparePart
        fields = (
            'pk', 'name', 'text', 'phone', 'price', 'created', 'img', 'checked',
            'category_name', 'address_name', 'part_number', 'brand', 'model',
            'condition', 'thumbnail_url'
        )


class SparePartDetailSerializer(BaseProductDetailSerializer):
    part_number = serializers.CharField(read_only=True)
    brand = serializers.CharField(read_only=True)
    model = serializers.CharField(read_only=True)
    year = serializers.IntegerField(read_only=True)
    condition = serializers.CharField(read_only=True)
    compatibility = serializers.CharField(read_only=True)

    class Meta:
        model = SparePart
        fields = (
            'pk', 'name', 'address_name', 'text', 'category_name', 'phone', 'price',
            'created', 'img', 'checked', 'part_number', 'brand', 'model', 'year',
            'condition', 'compatibility', 'images', 'thumbnail_url'
        )


class SparePartSerializer(serializers.ModelSerializer):
    category = serializers.IntegerField(write_only=True)
    address = serializers.IntegerField(write_only=True)
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = SparePart
        fields = (
            'pk', 'name', 'author', 'text', 'phone', 'price', 'img', 'created', 'checked',
            'category', 'address', 'part_number', 'brand', 'model', 'year',
            'condition', 'compatibility', 'images'
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

        for img in images_data:
            ImageSparePart.objects.create(sparepart=sparepart, img=img)

        return sparepart