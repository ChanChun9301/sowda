from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import (
    Address, LogistCategory, ServiceCategory, VehicleCategory, SparePartCategory,
    Logist, Service, Vehicle, SparePart,
    ImageLogist, ImageService, ImageVehicle, ImageSparePart,
    UserProd, CarouselImage, AuditLog
)


# ====================== YARDAMÇY FUNKSIÝALAR ======================
def image_preview(obj):
    """Umumy surat önizleme"""
    if obj.img:
        return format_html(
            '<img src="{}" width="60" height="60" style="border-radius: 6px; object-fit: cover;" />',
            obj.img.url
        )
    return "Surat ýok"
image_preview.short_description = 'Surat'


def main_image_preview(obj):
    """Esasy surat önizleme (modeliň özünde)"""
    if obj.img:
        return format_html(
            '<img src="{}" width="60" height="60" style="border-radius: 6px; object-fit: cover;" />',
            obj.img.url
        )
    return "Esasy surat ýok"
main_image_preview.short_description = 'Esasy surat'


# ====================== INLINE SURATLAR ======================
class BaseImageInline(admin.TabularInline):
    """Umumy surat inline – her model üçin ulanyň"""
    extra = 1
    fields = ('img', 'image_thumb')
    readonly_fields = ('image_thumb',)

    def image_thumb(self, obj):
        if obj.img:
            return format_html(
                '<img src="{}" width="100" height="auto" style="border-radius: 4px;" />',
                obj.img.url
            )
        return "Surat ýok"
    image_thumb.short_description = 'Önizleme'


class ImageLogistInline(BaseImageInline):
    model = ImageLogist


class ImageServiceInline(BaseImageInline):
    model = ImageService


class ImageVehicleInline(BaseImageInline):
    model = ImageVehicle


class ImageSparePartInline(BaseImageInline):
    model = ImageSparePart


# ====================== ADDRESS ======================
class AddressInline(admin.TabularInline):
    model = Address
    fk_name = 'parent'
    extra = 1
    fields = ('name',)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)
    inlines = [AddressInline]
    list_per_page = 30


# ====================== KATEGORIÝALAR (agajy) ======================
class CategoryInline(admin.TabularInline):
    model = None  # Dinamiki
    fk_name = 'parent'
    extra = 1
    fields = ('name',)


class BaseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)
    inlines = [CategoryInline]
    list_per_page = 30


@admin.register(LogistCategory)
class LogistCategoryAdmin(BaseCategoryAdmin):
    pass


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(BaseCategoryAdmin):
    pass


@admin.register(VehicleCategory)
class VehicleCategoryAdmin(BaseCategoryAdmin):
    pass


@admin.register(SparePartCategory)
class SparePartCategoryAdmin(BaseCategoryAdmin):
    pass


# ====================== LOGISTIKA ======================
@admin.register(Logist)
class LogistAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'author', 'category', 'phone', 'price',
        'nirden', 'where', 'checked', 'created', main_image_preview
    )
    list_display_links = ('name', 'author')
    list_filter = ('checked', 'category', 'address', 'vip', 'bring', 'created')
    search_fields = ('name', 'author', 'phone', 'text', 'nirden', 'where')
    readonly_fields = ('created', 'main_image_form_preview')
    inlines = [ImageLogistInline]
    list_per_page = 25

    fieldsets = (
        (None, {
            'fields': ('name', 'category', 'author', 'phone', 'price', 'checked', 'vip')
        }),
        ('Logistika maglumatlary', {
            'fields': ('nirden', 'where', 'last_date', 'bring', 'address'),
            'description': 'Nireden, nire, haçan, nädip'
        }),
        ('Mazmun we surat', {
            'fields': ('text', 'img', 'main_image_form_preview'),
            'description': 'Esasy mazmun we surat'
        }),
        ('Koordinatalar', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Wagt', {
            'fields': ('created',),
            'classes': ('collapse',)
        }),
    )

    def main_image_form_preview(self, obj):
        if obj.img:
            return format_html(
                '<img src="{}" width="300" height="auto" style="border: 1px solid #ddd; border-radius: 6px;" />',
                obj.img.url
            )
        return "Esasy surat ýok"
    main_image_form_preview.short_description = 'Häzirki surat'


# ====================== HYZMATLAR ======================
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'category', 'phone', 'price', 'checked', main_image_preview)
    list_display_links = ('name', 'author')
    list_filter = ('checked', 'category', 'address', 'created')
    search_fields = ('name', 'author', 'phone', 'text')
    readonly_fields = ('created', 'main_image_form_preview')
    inlines = [ImageServiceInline]
    list_per_page = 25

    fieldsets = (
        (None, {
            'fields': ('name', 'category', 'author', 'phone', 'price', 'checked')
        }),
        ('Mazmun we surat', {
            'fields': ('text', 'img', 'main_image_form_preview')
        }),
        ('Ýerleşýän ýeri', {
            'fields': ('address',),
        }),
        ('Wagt', {
            'fields': ('created',),
            'classes': ('collapse',)
        }),
    )

    def main_image_form_preview(self, obj):
        if obj.img:
            return format_html(
                '<img src="{}" width="300" height="auto" style="border: 1px solid #ddd; border-radius: 6px;" />',
                obj.img.url
            )
        return "Esasy surat ýok"
    main_image_form_preview.short_description = 'Häzirki surat'


# ====================== ULAGLAR ======================
@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'category', 'phone', 'price', 'checked', main_image_preview)
    list_display_links = ('name', 'author')
    list_filter = ('checked', 'category', 'address', 'current_addr', 'created')
    search_fields = ('name', 'author', 'phone', 'text')
    readonly_fields = ('created', 'main_image_form_preview')
    inlines = [ImageVehicleInline]
    list_per_page = 25

    fieldsets = (
        (None, {
            'fields': ('name', 'category', 'author', 'phone', 'price', 'checked')
        }),
        ('Ýerleşýän ýerler', {
            'fields': ('address', 'current_addr'),
        }),
        ('Mazmun we surat', {
            'fields': ('text', 'img', 'main_image_form_preview')
        }),
        ('Koordinatalar', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Wagt', {
            'fields': ('created',),
            'classes': ('collapse',)
        }),
    )

    def main_image_form_preview(self, obj):
        if obj.img:
            return format_html(
                '<img src="{}" width="300" height="auto" style="border: 1px solid #ddd; border-radius: 6px;" />',
                obj.img.url
            )
        return "Esasy surat ýok"
    main_image_form_preview.short_description = 'Häzirki surat'


# ====================== ÄTIÝAÇLYK ŞAÝLARY ======================
@admin.register(SparePart)
class SparePartAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'author', 'category', 'brand', 'model', 'year',
        'condition', 'price', 'checked', main_image_preview
    )
    list_display_links = ('name', 'author')
    list_filter = ('checked', 'category', 'brand', 'condition', 'year', 'created')
    search_fields = ('name', 'author', 'brand', 'model', 'part_number', 'text')
    readonly_fields = ('created', 'main_image_form_preview')
    inlines = [ImageSparePartInline]
    list_per_page = 25

    fieldsets = (
        (None, {
            'fields': ('name', 'category', 'author', 'price', 'checked')
        }),
        ('Şaý maglumatlary', {
            'fields': ('part_number', 'brand', 'model', 'year', 'condition', 'compatibility')
        }),
        ('Mazmun we surat', {
            'fields': ('text', 'img', 'main_image_form_preview')
        }),
        ('Ýerleşýän ýeri', {
            'fields': ('address',),
        }),
        ('Wagt', {
            'fields': ('created',),
            'classes': ('collapse',)
        }),
    )

    def main_image_form_preview(self, obj):
        if obj.img:
            return format_html(
                '<img src="{}" width="300" height="auto" style="border: 1px solid #ddd; border-radius: 6px;" />',
                obj.img.url
            )
        return "Esasy surat ýok"
    main_image_form_preview.short_description = 'Häzirki surat'


# ====================== GALAN MODELLER ======================
@admin.register(UserProd)
class UserProdAdmin(admin.ModelAdmin):
    list_display = ('author', 'checked', 'sms_sent_at')
    list_filter = ('checked', 'sms_sent_at')
    search_fields = ('author',)
    readonly_fields = ('sms_sent_at',)
    list_per_page = 30


@admin.register(CarouselImage)
class CarouselImageAdmin(admin.ModelAdmin):
    list_display = ('name', image_preview)
    search_fields = ('name',)
    list_per_page = 20


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'model', 'timestamp')
    list_filter = ('action', 'model', 'timestamp')
    search_fields = ('user', 'action')
    readonly_fields = ('user', 'action', 'model', 'timestamp')
    list_per_page = 30

    def has_add_permission(self, request):
        return False  # Pozup bilmeýär


# ====================== ADMIN BAŞLYGY ======================
admin.site.site_title = 'Seýir Admin'
admin.site.site_header = 'Seýir – Admin Panel'
admin.site.index_title = 'Saýt dolandyryşy'