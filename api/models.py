from django.db import models
from django.conf import settings
from ckeditor.fields import RichTextField
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from datetime import datetime
import os

class UserProd(models.Model):
    author = models.CharField(max_length=8, unique=True)
    checked = models.BooleanField(default=False)
    sms_sent_at = models.DateTimeField(null=True, blank=True)
    # sms_code = models.CharField(max_length=6, null=True, blank=True)  # eger gerek bolsa

    def is_sms_valid(self):
        if not self.sms_sent_at:
            return False
        delta = timezone.now() - self.sms_sent_at
        return delta <= timedelta(minutes=10)
        
# ====================== UTILS ======================

def get_upload_path(instance, filename, base_dir):
    """Dinamiki ýol: base_dir/yyyyMMdd_HHmm_name/filename"""
    now = datetime.now().strftime("%Y%m%d_%H%M")
    name = instance.name or "unknown"
    return f'{base_dir}/{now}_{name}/{filename}'


def generate_thumbnail(image_field, size=(300, 300)):
    """Thumbnail döredýär"""
    if not image_field:
        return None
    img = Image.open(image_field).convert('RGB')
    img.thumbnail(size)
    thumb_io = BytesIO()
    img.save(thumb_io, 'JPEG', quality=85)
    filename = os.path.basename(image_field.name)
    return ContentFile(thumb_io.getvalue(), name=f'thumb_{filename}')


# ====================== BASE MODELS ======================

class BaseCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Ady'))
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='subcategories', verbose_name=_('Baş kategoriýa')
    )

    class Meta:
        abstract = True
        verbose_name = _('Kategoriýa')
        verbose_name_plural = _('Kategoriýalar')

    def __str__(self):
        return self.name


class BaseProduct(models.Model):
    name = models.CharField(max_length=150, blank=True, null=True, verbose_name=_('Ady'))
    address = models.ForeignKey('Address', on_delete=models.CASCADE, verbose_name=_('Salgy'))
    author = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Awtor'))
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name=_('Telefon'))
    img = models.ImageField(
        upload_to=lambda i, f: get_upload_path(i, f, 'products'),
        null=True, blank=True, verbose_name=_('Surat')
    )
    text = RichTextField(null=True, blank=True, verbose_name=_('Giňişleýin'))
    price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, verbose_name=_('Bahasy')
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('Döredilen wagty'))
    checked = models.BooleanField(default=False, verbose_name=_('Barlandy'))
    thumbnail = models.ImageField(upload_to='products/thumbnails/', blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ['-created', 'checked']

    def save(self, *args, **kwargs):
        if self.img and not self.thumbnail:
            self.thumbnail = generate_thumbnail(self.img)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name or _('Ady ýok')


class BaseImage(models.Model):
    img = models.ImageField(
        upload_to=lambda i, f: get_upload_path(i, f, 'products/multi'),
        verbose_name=_('Surat')
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ['-created']

    def __str__(self):
        try:
            return f'{settings.HOSTNAME}{self.img.url}'
        except:
            return _('Surat ýok')


# ====================== ADDRESS ======================

class Address(MPTTModel):
    name = models.CharField(max_length=100, verbose_name=_('Salgy'))
    parent = TreeForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='subaddresses', verbose_name=_('Baş salgy')
    )

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name


# ====================== KATEGORIÝALAR ======================

class LogistCategory(BaseCategory):
    class Meta(BaseCategory.Meta):
        verbose_name = _("Logistika kategoriýasy")
        verbose_name_plural = _("Logistika kategoriýalar")


class ServiceCategory(BaseCategory):
    class Meta(BaseCategory.Meta):
        verbose_name = _("Hyzmat kategoriýasy")
        verbose_name_plural = _("Hyzmat kategoriýalar")


class VehicleCategory(BaseCategory):
    class Meta(BaseCategory.Meta):
        verbose_name = _("Ulag kategoriýasy")
        verbose_name_plural = _("Ulag kategoriýalar")


class SparePartCategory(BaseCategory):
    class Meta(BaseCategory.Meta):
        verbose_name = _("Ätiýaçlyk şaý kategoriýasy")
        verbose_name_plural = _("Ätiýaçlyk şaý kategoriýalar")


# ====================== ESASY MODELLER (4 SANY) ======================

# 1. Logistika
class Logist(BaseProduct):
    category = models.ForeignKey(LogistCategory, on_delete=models.CASCADE, verbose_name=_('Kategoriýa'))
    where = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('Nire'))
    nirden = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('Nireden'))
    last_date = models.DateField(null=True, blank=True, verbose_name=_('Soňky sene'))
    bring = models.BooleanField(default=False, verbose_name=_('Getir'))
    vip = models.BooleanField(default=False, verbose_name=_('VIP'))
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name=_("Eni"))
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name=_("Uzynlygy"))

    class Meta(BaseProduct.Meta):
        verbose_name = _("Logistika")
        verbose_name_plural = _("Logistikalar")


class ImageLogist(BaseImage):
    logist = models.ForeignKey(Logist, on_delete=models.CASCADE, related_name='images', verbose_name=_('Haryt'))


# 2. Hyzmatlar
class Service(BaseProduct):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, verbose_name=_('Kategoriýa'))

    class Meta(BaseProduct.Meta):
        verbose_name = _("Hyzmat")
        verbose_name_plural = _("Hyzmatlar")


class ImageService(BaseImage):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='images', verbose_name=_('Haryt'))


# 3. Ulaglar
class Vehicle(BaseProduct):
    category = models.ForeignKey(VehicleCategory, on_delete=models.CASCADE, verbose_name=_('Kategoriýa'))
    current_addr = models.ForeignKey(
        Address, on_delete=models.CASCADE, related_name='current_vehicles',
        verbose_name=_('Häzirki salgy')
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name=_("Eni"))
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name=_("Uzynlygy"))

    class Meta(BaseProduct.Meta):
        verbose_name = _("Ulag")
        verbose_name_plural = _("Ulaglar")


class ImageVehicle(BaseImage):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='images', verbose_name=_('Haryt'))


# 4. Awtoulaglaryň ätiýaçlyk şaýlary (Zapçastlar)
class SparePart(BaseProduct):
    category = models.ForeignKey(SparePartCategory, on_delete=models.CASCADE, verbose_name=_('Kategoriýa'))
    
    # Ätiýaçlyk şaýlaryna mahsus meýdanlar
    part_number = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Zapçast belgisi'))
    brand = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Marka'))
    model = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Model'))
    year = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Ýyl'))
    condition = models.CharField(
        max_length=20,
        choices=[
            ('new', _('Täze')),
            ('used', _('Ulanylan')),
            ('refurbished', _('Dikelden')),
        ],
        default='used',
        verbose_name=_('Ýagdaýy')
    )
    compatibility = models.TextField