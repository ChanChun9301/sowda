import os
import uuid
from datetime import datetime, timedelta
from io import BytesIO

from ckeditor.fields import RichTextField
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey
from PIL import Image

# ====================== UTILS & UPLOAD PATHS ======================

def get_upload_path(instance, filename, base_dir):
    """Dinamiki ýol: base_dir/yyyyMMdd_HHmm_uuid/filename"""
    now = datetime.now().strftime("%Y%m%d_%H%M")
    # Unikal bolar ýaly we ID meselesini çözmek üçin gysga uuid ulanýarys
    unique_id = uuid.uuid4().hex[:6]
    ext = os.path.splitext(filename)[1]
    secure_filename = f"{unique_id}{ext}"
    return f'{base_dir}/{now}_{unique_id}/{secure_filename}'

def logist_upload_path(instance, filename): return get_upload_path(instance, filename, 'products/logist')
def service_upload_path(instance, filename): return get_upload_path(instance, filename, 'products/service')
def vehicle_upload_path(instance, filename): return get_upload_path(instance, filename, 'products/vehicle')
def sparepart_upload_path(instance, filename): return get_upload_path(instance, filename, 'products/sparepart')
def carousel_upload_path(instance, filename): return get_upload_path(instance, filename, 'products/carousel')
def top_product_upload_path(instance, filename): return get_upload_path(instance, filename, 'top_products')
def multi_image_upload_path(instance, filename):
    base = f'products/multi/{instance.__class__.__name__.lower()}'
    return get_upload_path(instance, filename, base)

def generate_thumbnail(image_field, size=(300, 300)):
    """Thumbnail döredýär we WEBP formatda ýatda saklaýar (Flutter tarapda çalt açylmagy üçin)"""
    if not image_field:
        return None
    try:
        img = Image.open(image_field).convert('RGB')
        img.thumbnail(size)
        thumb_io = BytesIO()
        img.save(thumb_io, 'WEBP', quality=80)
        filename = os.path.splitext(os.path.basename(image_field.name))[0] + '_thumb.webp'
        return ContentFile(thumb_io.getvalue(), name=filename)
    except Exception:
        return None

def compress_image(image_field, quality=80):
    """Esasy suratlary hem WEBP görnüşine geçirip gysmak üçin"""
    if not image_field:
        return None
    try:
        img = Image.open(image_field).convert('RGB')
        img_io = BytesIO()
        img.save(img_io, 'WEBP', quality=quality, method=6)
        filename = os.path.splitext(os.path.basename(image_field.name))[0] + '.webp'
        return ContentFile(img_io.getvalue(), name=filename)
    except Exception:
        return image_field


# ====================== USERS & ADDRESS ======================

class UserProd(models.Model):
    author = models.CharField(max_length=8, unique=True)
    phone_model = models.CharField(max_length=8, null=True, blank=True)
    checked = models.BooleanField(default=False)
    sms_sent_at = models.DateTimeField(null=True, blank=True)

    def is_sms_valid(self):
        if not self.sms_sent_at:
            return False
        return timezone.now() - self.sms_sent_at <= timedelta(minutes=10)

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


# ====================== BASE MODELS ======================

class BaseCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Ady'))
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='%(class)s_subcategories', verbose_name=_('Baş kategoriýa')
    )

    class Meta:
        abstract = True
        verbose_name = _('Kategoriýa')
        verbose_name_plural = _('Kategoriýalar')

    def __str__(self):
        return self.name

class BaseProduct(models.Model):
    name = models.CharField(max_length=150, blank=True, null=True, verbose_name=_('Ady'))
    address = models.ForeignKey(Address, on_delete=models.CASCADE, verbose_name=_('Salgy'))
    author = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Awtor'))
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name=_('Telefon'))
    text = RichTextField(null=True, blank=True, verbose_name=_('Giňişleýin'))
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name=_('Bahasy'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('Döredilen wagty'))
    checked = models.BooleanField(default=False, verbose_name=_('Barlandy'))
    thumbnail = models.ImageField(upload_to='products/thumbnails/', blank=True, null=True, editable=False)

    class Meta:
        abstract = True
        ordering = ['-checked', '-created']

    def save(self, *args, **kwargs):
        # Surat bar bolsa we heniz thumbnail döredilmedik bolsa
        if hasattr(self, 'img') and self.img and not self.thumbnail:
            self.thumbnail = generate_thumbnail(self.img)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name or _('Ady ýok')

class BaseImage(models.Model):
    img = models.ImageField(upload_to=multi_image_upload_path, verbose_name=_('Surat'))
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ['-created']

    def __str__(self):
        return f'{settings.HOSTNAME}{self.img.url}' if self.img else _('Surat ýok')


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


# ====================== ESASY MODELLER ======================

# 1. Logistika
class Logist(BaseProduct):
    category = models.ForeignKey(LogistCategory, on_delete=models.CASCADE, verbose_name=_('Kategoriýa'))
    where = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('Nire'))
    nirden = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('Nireden'))
    last_date = models.DateField(null=True, blank=True, verbose_name=_('Soňky sene'))
    bring = models.BooleanField(default=False, verbose_name=_('Getir'))
    vip = models.BooleanField(default=False, verbose_name=_('VIP'))
    is_client = models.BooleanField(default=False, verbose_name=_('Müşderi'))
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name=_("Ini"))
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name=_("Uzynlygy"))
    img = models.ImageField(upload_to=logist_upload_path, null=True, blank=True)
    
    class Meta(BaseProduct.Meta):
        verbose_name = _("Logistika")
        verbose_name_plural = _("Logistikalar")

class ImageLogist(BaseImage):
    logist = models.ForeignKey(Logist, on_delete=models.CASCADE, related_name='images', verbose_name=_('Haryt'))


# 2. Hyzmatlar
class Service(BaseProduct):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, verbose_name=_('Kategoriýa'))
    img = models.ImageField(upload_to=service_upload_path, null=True, blank=True)

    class Meta(BaseProduct.Meta):
        verbose_name = _("Hyzmat")
        verbose_name_plural = _("Hyzmatlar")

class ImageService(BaseImage):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='images', verbose_name=_('Haryt'))


# 3. Ulaglar
class Vehicle(BaseProduct):
    year = models.PositiveIntegerField(verbose_name=_("Ýyly"))
    color = models.CharField(max_length=50, verbose_name=_("Reňki"))
    engine_volume = models.DecimalField(max_digits=3, decimal_places=1, verbose_name=_("Motor göwrümi"))
    mileage = models.PositiveIntegerField(verbose_name=_("Ýörelen ýoly (km)"))
    
    GEARBOX_CHOICES = (
        ('manual', _('Mehanika')),
        ('automatic', _('Awtomat')),
        ('hybrid', _('Gibrid')),
    )
    gearbox = models.CharField(max_length=20, choices=GEARBOX_CHOICES, verbose_name=_("Geçiriji guty (Korobka)"))
    
    FUEL_CHOICES = (
        ('gasoline', _('Benzin')),
        ('diesel', _('Dizel')),
        ('electric', _('Elektrik')),
        ('hybrid', _('Gibrid')),
    )
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, verbose_name=_("Ýangyç görnüşi"))

    vin_code = models.CharField(max_length=17, unique=True, null=True, blank=True, verbose_name=_("VIN kody"))
    category = models.ForeignKey(VehicleCategory, on_delete=models.CASCADE, verbose_name=_('Kategoriýa'))
    current_addr = models.ForeignKey(
        Address, on_delete=models.CASCADE, related_name='current_vehicles',
        verbose_name=_('Häzirki salgy')
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name=_("Eni"))
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name=_("Uzynlygy"))
    img = models.ImageField(upload_to=vehicle_upload_path, null=True, blank=True)

    class Meta(BaseProduct.Meta):
        verbose_name = _("Ulag")
        verbose_name_plural = _("Ulaglar")

class ImageVehicle(BaseImage):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='images', verbose_name=_('Haryt'))


# 4. Zapçastlar
class SparePart(BaseProduct):
    category = models.ForeignKey(SparePartCategory, on_delete=models.CASCADE, verbose_name=_('Kategoriýa'))
    img = models.ImageField(upload_to=sparepart_upload_path, null=True, blank=True)
    part_number = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Zapçast belgisi'))
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
    compatibility = models.TextField(blank=True, null=True, verbose_name=_('Sazlaşyklygy'))

    class Meta(BaseProduct.Meta):
        verbose_name = _("Ätiýaçlyk şaý")
        verbose_name_plural = _("Ätiýaçlyk şaýlar")

class ImageSparePart(BaseImage):
    sparepart = models.ForeignKey(SparePart, on_delete=models.CASCADE, related_name='images', verbose_name=_('Ätiýaçlyk şaý'))


# ====================== CAROUSEL & TOP PRODUCTS ======================

class CarouselImage(models.Model):
    name = models.CharField(max_length=150, blank=True, null=True, verbose_name=_('Ady'))
    description = RichTextField(blank=True, null=True, verbose_name=_('Giňişleýin'))
    img = models.ImageField(upload_to=carousel_upload_path, verbose_name=_('Surat'))
    link = models.URLField(max_length=500, blank=True, null=True, verbose_name=_('Baglanyşyk'))
    is_active = models.BooleanField(default=True, verbose_name=_('Işjeň'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Tertip'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('Döredilen wagty'))

    class Meta:
        verbose_name = _("Karusel suraty")
        verbose_name_plural = _("Karusel suratlary")
        ordering = ['order', '-created']

    def save(self, *args, **kwargs):
        if self.img:
            # Döretmek we täzelemek wagtynda suraty WEBP formatda gysýar
            self.img = compress_image(self.img)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name or f"Carousel #{self.pk}"

class TopProduct(BaseProduct):
    category = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Kategoriýa'))
    img = models.ImageField(upload_to=top_product_upload_path, null=True, blank=True)

    class Meta(BaseProduct.Meta):
        verbose_name = _("Top Haryt")
        verbose_name_plural = _("Top Harytlar")

class ImageTopProduct(BaseImage):
    top_product = models.ForeignKey(TopProduct, on_delete=models.CASCADE, related_name='images', verbose_name=_('Suratlar'))
