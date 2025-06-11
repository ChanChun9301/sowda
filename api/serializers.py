from django.contrib.auth.models import User
from rest_framework import serializers
from .models import *
from .functions import user_created


class RefreshSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    username = serializers.CharField()


class CarouselSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarouselImage
        fields = ('pk', 'name', 'img')


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = UserProd
        fields = ['id', 'author', 'password', 'checked']
        read_only_fields = ['checked']

    def create(self, validated_data):
        user = UserProd.objects.create_user(
            username=validated_data['author'],
            password=validated_data['password']
        )
        return user


class UserCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = UserProd
        fields = ('author', 'username', 'password')


class AddressSerializer(serializers.ModelSerializer):
    subaddresses = serializers.SerializerMethodField()

    class Meta:
        model = Address
        fields = ('pk', 'name', 'parent', 'subaddresses')

    def get_subaddresses(self, obj):
        children = obj.subaddresses.all()
        return AddressSerializer(children, many=True).data


class NewsCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsCategory
        fields = ('pk', 'name')


class ImageTopSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = ImageTop
        fields = ['url']

    def get_url(self, obj):
        request = self.context.get('request')
        if obj.img and hasattr(obj.img, 'url'):
            url = obj.img.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None


class TopProductsSerializer(serializers.ModelSerializer):
    address_name = serializers.CharField(source='address.name', read_only=True)

    class Meta:
        model = TopProducts
        fields = ('pk', 'name', 'address_name', 'text', 'phone', 'price', 'created', 'img', 'checked','thumbnail')


class TopProductDetailSerializer(serializers.ModelSerializer):
    images = ImageTopSerializer(many=True, read_only=True)
    address = serializers.CharField(source='address.name', read_only=True)

    class Meta:
        model = TopProducts
        fields = ['pk', 'name', 'address', 'text', 'category', 'phone', 'price', 'created', 'img', 'checked', 'images']


class NewsSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = News
        fields = ('pk', 'name', 'img', 'author', 'text', 'category', 'created', 'checked')


class ImageCarSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageCar
        fields = ['img']


class CarCategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = CarCategory
        fields = ('pk', 'name', 'parent', 'subcategories')

    def get_subcategories(self, obj):
        children = obj.subcategories.all()
        return CarCategorySerializer(children, many=True).data


class CarDetailSerializer(serializers.ModelSerializer):
    category = serializers.CharField()
    address = serializers.CharField()
    images = serializers.StringRelatedField(many=True)

    class Meta:
        model = Car
        fields = ('pk', 'name', 'address', 'text', 'category', 'phone', 'price', 'created', 'img', 'images')


class CarListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name')
    address_name = serializers.CharField(source='address.name')

    class Meta:
        model = Car
        fields = ('pk', 'name', 'text', 'phone', 'price', 'created', 'img', 'checked', 'address_name', 'category_name')


class CarSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.id')
    address = serializers.CharField(source='address.id')
    images = serializers.ListField(child=serializers.ImageField(), write_only=True)

    def create(self, validated_data):
        address_data = validated_data.pop('address')
        category_data = validated_data.pop('category')
        images_data = validated_data.pop('images')
        category = CarCategory.objects.get(id=int(category_data['id']))
        address = Address.objects.get(id=int(address_data['id']))
        car = Car.objects.create(category=category, address=address, **validated_data)

        for image in images_data:
            ImageCar.objects.create(car=car, img=image)

        return car

    class Meta:
        model = Car
        fields = ('pk', 'name', 'address', 'author', 'text', 'phone', 'price', 'created', 'img', 'category', 'images')


class ImageElinSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageElin
        fields = ['img']


class ElinCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ElinCategory
        fields = ('pk', 'name')


class ElinDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name')
    address_name = serializers.CharField(source='address.name')
    images = serializers.StringRelatedField(many=True)

    class Meta:
        model = Elin
        fields = ('pk', 'name', 'address_name', 'text', 'category_name', 'phone', 'price', 'created', 'img', 'images', 'checked')


class ElinListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name')
    address_name = serializers.CharField(source='address.name')

    class Meta:
        model = Elin
        fields = ('pk', 'name', 'text', 'phone', 'price', 'created', 'img', 'checked', 'author', 'category_name', 'address_name')


class ElinSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.id')
    address = serializers.CharField(source='address.id')
    images = serializers.ListField(child=serializers.ImageField(), write_only=True)

    def create(self, validated_data):
        address_data = validated_data.pop('address')
        category_data = validated_data.pop('category')
        images_data = validated_data.pop('images')
        category = ElinCategory.objects.get(id=int(category_data['id']))
        address = Address.objects.get(id=int(address_data['id']))
        elin = Elin.objects.create(category=category, address=address, **validated_data)

        for image in images_data:
            ImageElin.objects.create(elin=elin, img=image)

        return elin

    class Meta:
        model = Elin
        fields = ('pk', 'name', 'address', 'text', 'phone', 'price', 'created', 'img', 'checked', 'category', 'author', 'images')


class ImageLogistSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageLogist
        fields = ['img']

class LogistCategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = LogistCategory
        fields = ('pk', 'name', 'subcategories')

    def get_subcategories(self, obj):
        subcats = obj.subcategories.all()
        return LogistCategoryChildSerializer(subcats, many=True).data



class LogistCategoryChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogistCategory
        fields = ('pk', 'name')

class ImageLogistCarSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageLogistCar
        fields = ['img']

class LogistCarDetailSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name')
    address = serializers.CharField(source='address.name')
    images = serializers.StringRelatedField(many=True)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, read_only=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, read_only=True)

    class Meta:
        model = LogistCar
        fields = ('pk', 'name', 'address', 'text', 'category', 'last_date', 'where', 'nirden',
                  'bring', 'vip', 'phone', 'price', 'url', 'created', 'img', 'checked', 'images',
                  'latitude', 'longitude')

class LogistCarListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name')
    address_name = serializers.CharField(source='address.name')
    current_address_name = serializers.CharField(source='current_addr.name')
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, read_only=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, read_only=True)

    class Meta:
        model = LogistCar
        fields = (
            'pk', 'name', 'text', 'phone', 'price', 'created', 'img', 'checked',
            'category_name', 'address_name', 'current_address_name',
            'latitude', 'longitude'
        )


class LogistCarSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.id')
    address = serializers.CharField(source='address.id')
    current_addr = serializers.CharField(source='current_addr.id')
    category_name = serializers.CharField(source='category.name', read_only=True)
    address_name = serializers.CharField(source='address.name', read_only=True)
    current_address_name = serializers.CharField(source='current_addr.name', read_only=True)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)

    def create(self, validated_data):
        category_data = validated_data.pop('category')
        address_data = validated_data.pop('address')
        current_addr_data = validated_data.pop('current_addr')
        latitude = validated_data.pop('latitude', None)
        longitude = validated_data.pop('longitude', None)

        category = LogistCategory.objects.get(id=int(category_data['id']))
        address = Address.objects.get(id=int(address_data['id']))
        current_addr = Address.objects.get(id=int(current_addr_data['id']))

        logist_car = LogistCar.objects.create(
            category=category,
            address=address,
            current_addr=current_addr,
            latitude=latitude,
            longitude=longitude,
            **validated_data
        )

        return logist_car

    class Meta:
        model = LogistCar
        fields = (
            'pk', 'name', 'author', 'text', 'phone', 'price', 'img', 'created', 'checked',
            'category', 'address', 'current_addr',
            'latitude', 'longitude',
            'category_name', 'address_name', 'current_address_name'
        )



class LogistDetailSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name')
    address = serializers.CharField(source='address.name')
    images = serializers.StringRelatedField(many=True)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, read_only=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, read_only=True)

    class Meta:
        model = Logist
        fields = ('pk', 'name', 'address', 'text', 'category', 'last_date', 'where', 'nirden',
                  'bring', 'vip', 'phone', 'price', 'url', 'created', 'img', 'checked', 'images',
                  'latitude', 'longitude')


class LogistListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name')
    address_name = serializers.CharField(source='address.name')
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, read_only=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, read_only=True)

    class Meta:
        model = Logist
        fields = ('pk', 'name', 'text', 'phone', 'price', 'created', 'last_date', 'where',
                  'nirden', 'bring', 'vip', 'img', 'checked', 'address_name', 'category_name',
                  'latitude', 'longitude')


class LogistSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.id')
    address = serializers.CharField(source='address.id')
    category_name = serializers.CharField(source='category.name')
    address_name = serializers.CharField(source='address.name')
    images = serializers.ListField(child=serializers.ImageField(), write_only=True)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)

    def create(self, validated_data):
        address_data = validated_data.pop('address')
        category_data = validated_data.pop('category')
        images_data = validated_data.pop('images', [])
        latitude = validated_data.pop('latitude', None)
        longitude = validated_data.pop('longitude', None)

        category = LogistCategory.objects.get(id=int(category_data['id']))
        address = Address.objects.get(id=int(address_data['id']))

        logist = Logist.objects.create(
            category=category,
            address=address,
            latitude=latitude,
            longitude=longitude,
            **validated_data
        )

        for image in images_data:
            ImageLogist.objects.create(logist=logist, img=image)

        return logist

    class Meta:
        model = Logist
        fields = ('pk', 'name', 'author', 'address', 'text', 'phone', 'last_date', 'images',
                  'where', 'nirden', 'bring', 'vip', 'price', 'url', 'created', 'img', 'checked',
                  'category', 'latitude', 'longitude','category_name','address_name')


class ImageOtherSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageOther
        fields = ['img']


class OtherCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherCategory
        fields = ('pk', 'name')


class OtherDetailSerializer(serializers.ModelSerializer):
    category = serializers.CharField()
    address = serializers.CharField()
    images = serializers.StringRelatedField(many=True)

    class Meta:
        model = Other
        fields = ('pk', 'name', 'address', 'text', 'category', 'phone', 'price', 'created', 'img', 'images', 'checked')


class OtherListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name')
    address_name = serializers.CharField(source='address.name')

    class Meta:
        model = Other
        fields = ('pk', 'name', 'text', 'phone', 'price', 'created', 'img', 'checked', 'address_name', 'category_name')


class OtherSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.id')
    address = serializers.CharField(source='address.id')
    images = serializers.ListField(child=serializers.ImageField(), write_only=True)

    def create(self, validated_data):
        address_data = validated_data.pop('address')
        category_data = validated_data.pop('category')
        images_data = validated_data.pop('images')
        category = OtherCategory.objects.get(id=int(category_data['id']))
        address = Address.objects.get(id=int(address_data['id']))
        other = Other.objects.create(category=category, address=address, **validated_data)
        for image in images_data:
            ImageOther.objects.create(other=other, img=image)
        return other

    class Meta:
        model = Other
        fields = ('pk', 'name', 'address', 'text', 'phone', 'price', 'created', 'img', 'checked', 'category', 'author', 'images')


class ImageServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageService
        fields = ['img']


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ('pk', 'name')


class ServiceDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name')
    address_name = serializers.CharField(source='address.name')
    images = serializers.StringRelatedField(many=True)

    class Meta:
        model = Service
        fields = ('pk', 'name', 'address_name', 'text', 'category_name', 'phone', 'price', 'created', 'img', 'images', 'checked')


class ServiceListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name')
    address_name = serializers.CharField(source='address.name')
    images = serializers.ListField(child=serializers.ImageField(), write_only=True)

    class Meta:
        model = Service
        fields = ('pk', 'name', 'author', 'text', 'phone', 'price', 'created', 'img', 'checked', 'images', 'category_name', 'address_name')


class ServiceSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.id')
    address = serializers.CharField(source='address.id')
    images = serializers.ListField(child=serializers.ImageField(), write_only=True)

    def create(self, validated_data):
        address_data = validated_data.pop('address')
        category_data = validated_data.pop('category')
        images_data = validated_data.pop('images')
        category = ServiceCategory.objects.get(id=int(category_data['id']))
        address = Address.objects.get(id=int(address_data['id']))
        service = Service.objects.create(category=category, address=address, **validated_data)

        for image in images_data:
            ImageService.objects.create(service=service, img=image)

        return service

    class Meta:
        model = Service
        fields = ('pk', 'name', 'address', 'author', 'text', 'phone', 'price',
                  'created', 'img', 'checked', 'category', 'images')
