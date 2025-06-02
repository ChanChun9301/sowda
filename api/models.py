from django.db import models
from django.conf import settings
from ckeditor.fields import RichTextField
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils import timezone
from datetime import timedelta


class AuditLog(models.Model):
    user = models.CharField(max_length=255, null=True, blank=True)
    action = models.CharField(blank=True,max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp} - {self.user} - {self.action}"

class UserProd(models.Model):
    author = models.CharField(max_length=255, null=True)
    checked = models.BooleanField(default=False, verbose_name='Barlandy')

    class Meta:
        verbose_name = "Ulanyjy"
        verbose_name_plural = "Ulanyjylar"

    def __str__(self):
        return f'{self.author}'


class CarouselImage(models.Model):
    name = models.CharField(max_length=150,blank=True, verbose_name='Ady')
    img = models.ImageField(upload_to='carousel', null=True, verbose_name='Surat')

    class Meta:
        verbose_name = "Banner surat"
        verbose_name_plural = "Banner suratlar"

    def __str__(self):
        return self.name


class Address(MPTTModel):
    name = models.CharField(max_length=100,blank=True, null=True, verbose_name='Salgy')
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subaddresses',
        verbose_name='Baş salgy'
    )

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name


class TopProducts(models.Model):
    name = models.CharField(max_length=100,blank=True, null=True, verbose_name='Ady')
    category = models.CharField(max_length=100, null=True, verbose_name='Kategoriýa')
    author = models.CharField(max_length=255, null=True, verbose_name='Awtor')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name='Bahasy')
    address = models.ForeignKey(Address, on_delete=models.CASCADE, verbose_name='Salgy')
    text = RichTextField(null=True)
    phone = models.IntegerField(null=True, verbose_name='Telefon belgisi')
    img = models.ImageField(upload_to='top_product/', verbose_name='Surat', null=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name='Döredilen wagty')
    checked = models.BooleanField(default=False, verbose_name='Barlandy')
    thumbnail = models.ImageField(upload_to='top_product/thumbnails/', blank=True, null=True)

    class Meta:
        ordering = ['-created', 'checked']
        verbose_name = "Saýlanan"
        verbose_name_plural = "Saýlananlar"

    def __str__(self):
        return self.name or "Nämeleri ýok"


    def save(self, *args, **kwargs):
        if self.img and not self.thumbnail:
            self.thumbnail = self.make_thumbnail(self.img)
        super().save(*args, **kwargs)

    def make_thumbnail(self, image, size=(300, 300)):
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=85)

        thumbnail = ContentFile(thumb_io.getvalue(), name=image.name)
        return thumbnail

    @staticmethod
    def image_upload_path(instance, filename):
        now = datetime.now().strftime("%Y-%m-%d")
        return f'top_product/{now}-{instance.top.name}/{filename}'


class ImageTop(models.Model):
    top = models.ForeignKey(
        TopProducts,
        on_delete=models.CASCADE,
        null=True,
        related_name='images',
        verbose_name='Haryt'
    )
    img = models.ImageField(upload_to=TopProducts.image_upload_path, null=True, verbose_name='Surat')
    created = models.DateTimeField(auto_now_add=True, null=True, verbose_name='Döredilen wagty')

    class Meta:
        verbose_name = "Saýlanan surat"
        verbose_name_plural = "Saýlanan suratlar"

    def __str__(self):
        try:
            return f'{settings.HOSTNAME}{self.img.url}'
        except:
            return "Surat ýok"


class NewsCategory(models.Model):
    name = models.CharField(max_length=100, blank=True,null=True, verbose_name='Habar kategoriýasy')

    class Meta:
        verbose_name = "Habar kategoriýasy"
        verbose_name_plural = "Habar kategoriýalar"

    def __str__(self):
        return self.name


# models.py

from datetime import datetime

def image_add_habar(instance, filename):
    return f'habarlar/{datetime.now().strftime("%Y%m%d_%H%M")}_{filename}'

def image_add_top(instance, filename):
    return f'top_product/{datetime.now().strftime("%Y%m%d_%H%M")}_{filename}'

def images_add_top(instance, filename):
    return f'top_product/{datetime.now().strftime("%Y%m%d_%H%M")}_multi/{filename}'

class News(models.Model):
    name = models.CharField(max_length=500, blank=True,null=True, verbose_name='Ady')
    author = models.CharField(max_length=150, null=True, verbose_name='Awtor')
    category = models.ForeignKey(NewsCategory, on_delete=models.CASCADE, verbose_name='Kategoriýa')
    img = models.ImageField(upload_to='habarlar/', null=True, verbose_name='Surat')
    text = RichTextField(null=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name='Döredilen wagty')
    checked = models.BooleanField(default=False, verbose_name='Barlandy')

    class Meta:
        ordering = ['-created', 'checked']
        verbose_name = "Habar"
        verbose_name_plural = "Habarlar"

    def __str__(self):
        return self.name or "Ady ýok"



class CarCategory(models.Model):
    name = models.CharField(null=True,blank=True, max_length=100)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='subcategories',
        verbose_name="Baş kategoriýa"
    )

    class Meta:
        verbose_name = "Awtoulag kategoriýasy"
        verbose_name_plural = "Awtoulag kategoriýalar"

    def __str__(self):
        return self.name

def image_add_car(self,filename):
    return f'awtoulaglar/{self.created}-{self.name}/{filename}'
def images_add_car(self,filename):
    return f'awtoulaglar/{self.created}-{self.car.name}/{filename}'
class Car(models.Model):
    name = models.CharField(null=True, blank=True,max_length=100)
    address = models.ForeignKey(Address,on_delete=models.CASCADE)
    author = models.CharField(max_length=8,null=True)
    category = models.ForeignKey(CarCategory,on_delete=models.CASCADE)
    phone = models.IntegerField(null=True,)
    img = models.ImageField(upload_to=image_add_car,null=True)
    text = RichTextField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    checked = models.BooleanField(default=False,verbose_name='Barlandy')
    price = models.DecimalField(null=True,  max_digits=10,decimal_places=2,)
    
    class Meta:
        ordering= ['-created','checked']
        verbose_name = ("Awotulag")
        verbose_name_plural = ("Awtoulaglar")

    def __str__(self):
        return self.name


class ImageCar(models.Model):
    car = models.ForeignKey(Car,on_delete=models.CASCADE,verbose_name='Haryt',null=True,related_name='images')
    img = models.ImageField(upload_to=images_add_car,null=True,verbose_name='Surat')
    created = models.DateTimeField(auto_now_add=True,verbose_name='Döredilen wagty',null=True)

    class Meta:
        ordering= ['created']
        verbose_name = ("Awtoulag surat")
        verbose_name_plural = ("Awtoulag suratlar")

    def __str__(self):
        return f'{settings.HOSTNAME}{self.img.url}'


class ElinCategory(models.Model):
    name = models.CharField(null=True,blank=True, max_length=100)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='subcategories',
        verbose_name="Baş kategoriýa"
    )

    class Meta:
        verbose_name = "Elin kategoriýasy"
        verbose_name_plural = "Elin kategoriýalar"

    def __str__(self):
        return self.name

def image_add_elin(self,filename):
    return f'elin/{self.created}-{self.name}{filename}'

def images_add_elin(self,filename):
    return f'elin/{self.created}-{self.elin.name}{filename}'

class Elin(models.Model):
    name = models.CharField(null=True,blank=True, max_length=100)
    address = models.ForeignKey(Address,on_delete=models.CASCADE)
    category = models.ForeignKey(ElinCategory,on_delete=models.CASCADE)
    author = models.CharField(max_length=8,null=True)
    phone = models.IntegerField(null=True)
    img = models.ImageField(upload_to=image_add_elin,null=True)
    text =  RichTextField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    checked = models.BooleanField(default=False,verbose_name='Barlandy')
    price = models.DecimalField(null=True,  max_digits=10,decimal_places=2,)
    
    class Meta:
        ordering= ['-created','checked']
        verbose_name = ("Elin")
        verbose_name_plural = ("Elin")

    def __str__(self):
        return self.name

class ImageElin(models.Model):
    elin = models.ForeignKey(Elin,on_delete=models.CASCADE,verbose_name='Haryt',null=True,related_name='images')
    img = models.ImageField(upload_to=images_add_elin,null=True,verbose_name='Surat')
    created = models.DateTimeField(auto_now_add=True,verbose_name='Döredilen wagty',null=True)

    class Meta:
        ordering= ['-created']
        verbose_name = ("Elin surat")
        verbose_name_plural = ("Elin suratlar")

    def __str__(self):
        return f'{settings.HOSTNAME}/{self.img.url}'

class LogistCategory(models.Model):
    name = models.CharField(null=True, blank=True,max_length=100)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='subcategories',
        verbose_name="Baş kategoriýa"
    )

    class Meta:
        verbose_name = "Logist kategoriýasy"
        verbose_name_plural = "Logist kategoriýalar"

    def __str__(self):
        return self.name

def image_add_logist(self,filename):
    return f'logistika/{self.created}-{self.name}/{filename}'

def images_add_logist(self,filename):
    return f'logistika/{self.created}-{self.logist.name}/{filename}'

class Logist(models.Model):
    name = models.CharField(null=True,blank=True, max_length=100)
    category = models.ForeignKey(LogistCategory, on_delete=models.CASCADE)
    author = models.CharField(max_length=8, null=True)
    where = models.CharField(max_length=20, null=True)
    nirden = models.CharField(max_length=20, null=True)
    last_date = models.DateField(null=True)
    bring = models.BooleanField(default=False)
    vip = models.BooleanField(default=False)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    phone = models.IntegerField(null=True)
    img = models.ImageField(upload_to=image_add_logist, null=True)
    text = RichTextField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    checked = models.BooleanField(default=False,verbose_name='Barlandy')
    price = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Eni")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Uzynlygy")
    
    class Meta:
        ordering = ['checked', '-created']
        verbose_name = "Logistika"
        verbose_name_plural = "Logistikalar"

    def __str__(self):
        return self.name

    @property
    def thumbnail_url(self):
        return self.img.url

class ImageLogist(models.Model):
    logist = models.ForeignKey(Logist,on_delete=models.CASCADE,verbose_name='Haryt',null=True,related_name='images')
    img = models.ImageField(upload_to=images_add_logist,null=True,verbose_name='Surat')
    created = models.DateTimeField(auto_now_add=True,verbose_name='Döredilen wagty',null=True)

    class Meta:
        ordering= ['-created']
        verbose_name = ("Logistika surat")
        verbose_name_plural = ("Logistika suratlar")

    def __str__(self):
        return f'{settings.HOSTNAME}{self.img.url}'


class ServiceCategory(models.Model):
    name = models.CharField(null=True,blank=True, max_length=100)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='subcategories',
        verbose_name="Baş kategoriýa"
    )

    class Meta:
        verbose_name = "Hyzmatlar kategoriýasy"
        verbose_name_plural = "Hyzmatlar kategoriýalar"

    def __str__(self):
        return self.name

def image_add_hyzmat(self,filename):
    return f'hyzmatlar/{self.created}-{self.name}/{filename}'

def images_add_hyzmat(self,filename):
    return f'hyzmatlar/{self.created}-{self.service.name}/{filename}'

class Service(models.Model):
    name = models.CharField(null=True,blank=True, max_length=100)
    address = models.ForeignKey(Address,on_delete=models.CASCADE)
    category = models.ForeignKey(ServiceCategory,on_delete=models.CASCADE)
    author = models.CharField(max_length=8,null=True)
    phone = models.IntegerField(null=True)
    img = models.ImageField(upload_to=image_add_hyzmat,null=True)
    text =RichTextField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    checked = models.BooleanField(default=False,verbose_name='Barlandy')
    price = models.DecimalField(null=True,  max_digits=10,decimal_places=2,)
    
    class Meta:
        ordering= ['-created','checked']
        verbose_name = ("Hyzmatlar")
        verbose_name_plural = ("Hyzmatlar")

    def __str__(self):
        return self.name

class ImageService(models.Model):
    service = models.ForeignKey(Service,on_delete=models.CASCADE,verbose_name='Haryt',null=True,related_name='images')
    img = models.ImageField(upload_to=image_add_hyzmat,null=True,verbose_name='Surat')
    created = models.DateTimeField(auto_now_add=True,verbose_name='Döredilen wagty',null=True)

    class Meta:
        ordering= ['created']
        verbose_name = ("Hyzmat surat")
        verbose_name_plural = ("Hyzmat suratlar")

    def __str__(self):
        return f'{settings.HOSTNAME}{self.img.url}'


class OtherCategory(models.Model):
    name = models.CharField(null=True, blank=True,max_length=100)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='subcategories',
        verbose_name="Baş kategoriýa"
    )

    class Meta:
        verbose_name = "Beýleki kategoriýasy"
        verbose_name_plural = "Beýleki kategoriýalar"

    def __str__(self):
        return self.name

def image_add_beyleki(self,filename):
    return f'beyleki/{self.created}-{self.name}/{filename}'

def images_add_beyleki(self,filename):
    return f'beyleki/{self.created}-{self.other.name}/{filename}'

class Other(models.Model):
    name = models.CharField(null=True,blank=True, max_length=100)
    address = models.ForeignKey(Address,on_delete=models.CASCADE)
    category = models.ForeignKey(OtherCategory,on_delete=models.CASCADE)
    author = models.CharField(max_length=8,null=True)
    phone = models.IntegerField(null=True)
    img = models.ImageField(upload_to=image_add_beyleki,null=True)
    text =RichTextField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    checked = models.BooleanField(default=False,verbose_name='Barlandy')
    price = models.DecimalField(null=True,  max_digits=10,decimal_places=2,)
    
    class Meta:
        ordering= ['-created','checked']
        verbose_name = ("Beylekiler")
        verbose_name_plural = ("Beylekiler")

    def __str__(self):
        return self.name

class ImageOther(models.Model):
    other = models.ForeignKey(Other,on_delete=models.CASCADE,verbose_name='Haryt',null=True,related_name='images')
    img = models.ImageField(upload_to=images_add_beyleki,null=True,verbose_name='Surat')
    created = models.DateTimeField(auto_now_add=True,verbose_name='Döredilen wagty',null=True)

    class Meta:
        ordering= ['created']
        verbose_name = ("Beyleki surat")
        verbose_name_plural = ("Beyleki suratlar")

    def __str__(self):
        return f'{settings.HOSTNAME}{self.img.url}'