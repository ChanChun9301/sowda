from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import *
from django.contrib import admin
from django.utils.html import format_html

def logist_main_image_preview(obj):
    """Displays a thumbnail of the main 'img' field on the Logist list page."""
    if obj.img: # This refers to the 'img' field directly on the Logist model
        return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px;" />', obj.img.url)
    return "No Main Image"
logist_main_image_preview.short_description = 'Main Image'


def image_preview(obj):
    """Displays a thumbnail image in the list_display."""
    if obj.img: # Referencing the 'img' field from your Logist model
        return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px;" />', obj.img.url)
    return "No Image"
image_preview.short_description = 'Main Image' 

# --- Inline for Related Logist Images (ImageLogist) ---
class ImageLogistInline(admin.TabularInline):
    """
    Allows adding/editing multiple ImageLogist instances directly
    from the Logist admin page.
    """
    model = ImageLogist # Use your ImageLogist model here
    extra = 1 # Number of empty forms to show for new images
    fields = ('img', 'get_image_thumbnail') # 'description' if ImageLogist has one
    readonly_fields = ('get_image_thumbnail',)

    def get_image_thumbnail(self, instance):
        if instance.img: # This refers to the 'img' field on the ImageLogist model
            return format_html('<img src="{}" width="100" height="auto" style="border-radius: 3px;" />', instance.img.url)
        return "No Image"
    get_image_thumbnail.short_description = 'Thumbnail'


@admin.register(Logist)
class LogistAdmin(admin.ModelAdmin):
    # Fields to display in the Logist list view (table)
    list_display = (
        'name',
        'author_username', # Custom method for linked author
        'category',
        'phone',
        'price',
        'nirden',
        'where',
        'checked',
        'created',
        logist_main_image_preview, # Thumbnail for the main Logist image
    )

    # Fields that link to the detail view from the list view
    list_display_links = ('name', 'author_username')

    # Fields to create filter options in the right sidebar
    list_filter = (
        'checked',
        'category',
        'address',
        'vip',
        'bring',
        'created',
        'last_date', # Added last_date as a filter
    )

    # Fields to enable searching across in the admin list page
    search_fields = (
        'name',
        'author', # 'author' is a CharField in Logist, so search directly
        'phone',
        'description', # Assuming 'text' field is mapped to 'description' in serializer/context
        'nirden',
        'where',
    )

    # Fields that are read-only in the add/change form
    readonly_fields = (
        'created',
        'main_image_form_preview', # Custom method to display main image preview in the form
    )

    # Inlines to include related models (e.g., ImageLogist)
    inlines = [ImageLogistInline]

    # How many items per page in the list view
    list_per_page = 20

    # Define the order and grouping of fields in the add/change form
    fieldsets = (
        (None, {
            'fields': (
                'name',
                'category',
                'author',
                'phone',
                'price',
                'checked',
                'vip',
            )
        }),
        ('Logistics Details', {
            'fields': (
                'nirden',
                'where',
                'last_date',
                'bring',
                'address',
            ),
            'description': 'Details about origin, destination, and delivery.',
        }),
        ('Main Content & Image', { # Section for the primary text and image
            'fields': (
                'text', # Your RichTextField
                'img',  # The main image upload field for the Logist model
                'main_image_form_preview', # Display the preview here
            ),
            'description': 'Main description and primary image for this logist entry.',
        }),
        ('Location Coordinates', {
            'fields': (
                'latitude',
                'longitude',
            ),
            'classes': ('collapse',),
            'description': 'Geographical coordinates for the logist entry.',
        }),
        ('Timestamps', {
            'fields': (
                'created',
            ),
            'classes': ('collapse',),
        }),
    )

    # Custom method to get author's username for list_display and list_display_links
    def author_username(self, obj):
        # Since 'author' in Logist is a CharField, we just return its value.
        # If it were a ForeignKey to a User model, it would be 'obj.author.username' or similar.
        return obj.author
    author_username.short_description = 'Author'
    author_username.admin_order_field = 'author' # Allows sorting by this column

    # Custom method to display the main Logist image preview in the admin form
    def main_image_form_preview(self, obj):
        if obj.img: # Refers to the 'img' field on the Logist model itself
            return format_html('<img src="{}" width="200" height="auto" style="border: 1px solid #ddd; border-radius: 5px;" />', obj.img.url)
        return "No Main Image"
    main_image_form_preview.short_description = 'Current Main Image'

# Elin

class ElinImageInline(admin.StackedInline):
    model = ImageElin
    fields = ["img"]
    readonly_fields = ["image_tag"]

    def image_tag(self, obj):
        return image_preview(obj)
    image_tag.short_description = 'Surat'


class ElinAdmin(admin.ModelAdmin):
    list_display = ('author','name','price','phone', image_preview, 'checked')
    list_display_links = ('author','name')
    list_filter = ('checked',)
    search_fields = ('author','name','phone')
    inlines = [ElinImageInline]
    list_per_page = 20
    readonly_fields = ['img']

admin.site.register(Elin, ElinAdmin)


# Other

class OtherImageInline(admin.StackedInline):
    model = ImageOther
    fields = ["img"]
    readonly_fields = ["image_tag"]

    def image_tag(self, obj):
        return image_preview(obj)
    image_tag.short_description = 'Surat'


class OtherAdmin(admin.ModelAdmin):
    list_display = ('author','name','price','phone', image_preview, 'checked')
    list_display_links = ('author','name')
    list_filter = ('checked',)
    search_fields = ('author','name','phone')
    inlines = [OtherImageInline]
    list_per_page = 20
    readonly_fields = ['img']

admin.site.register(Other, OtherAdmin)


# Car

class CarImageInline(admin.StackedInline):
    model = ImageCar
    fields = ["img"]
    readonly_fields = ["image_tag"]

    def image_tag(self, obj):
        return image_preview(obj)
    image_tag.short_description = 'Surat'


class CarAdmin(admin.ModelAdmin):
    list_display = ('author', 'created', 'name', 'price', 'phone', image_preview, 'checked')
    list_display_links = ('author','name')
    list_filter = ('checked', 'created')
    search_fields = ('author','name','phone')
    inlines = [CarImageInline]
    list_per_page = 20
    readonly_fields = ['img']
    date_hierarchy = 'created'

admin.site.register(Car, CarAdmin)


# News

class NewsAdmin(admin.ModelAdmin):
    list_display = ('name', image_preview, 'checked')
    list_filter = ('checked',)
    search_fields = ('name',)
    list_per_page = 20
    readonly_fields = ['img']

admin.site.register(News, NewsAdmin)


# Service

class ServiceImageInline(admin.StackedInline):
    model = ImageService
    fields = ["img"]
    readonly_fields = ["image_tag"]

    def image_tag(self, obj):
        return image_preview(obj)
    image_tag.short_description = 'Surat'


class ServiceAdmin(admin.ModelAdmin):
    list_display = ('author','name','price','phone', image_preview, 'checked')
    list_display_links = ('author','name')
    list_filter = ('checked',)
    search_fields = ('author','name','phone')
    inlines = [ServiceImageInline]
    list_per_page = 20
    readonly_fields = ['img']

admin.site.register(Service, ServiceAdmin)


# TopProducts

class TopImageInline(admin.StackedInline):
    model = ImageTop
    fields = ["img"]
    readonly_fields = ["image_tag"]

    def image_tag(self, obj):
        return image_preview(obj)
    image_tag.short_description = 'Surat'


class TopProductsAdmin(admin.ModelAdmin):
    list_display = ('name','author','price','phone', image_preview, 'checked')
    list_display_links = ('name',)
    list_filter = ('checked',)
    search_fields = ('name','author','phone')
    inlines = [TopImageInline]
    list_per_page = 20
    readonly_fields = ['img']

admin.site.register(TopProducts, TopProductsAdmin)


# Carousel

class CarouselAdmin(admin.ModelAdmin):
    list_display = ('name','pk', image_preview)
    list_display_links = ('name',)
    list_per_page = 20
    readonly_fields = ['img']

admin.site.register(CarouselImage, CarouselAdmin)


# Address with inline for child addresses

class AddressInline(admin.TabularInline):
    model = Address
    extra = 1
    fk_name = 'parent'  # Kiçi salgylary parent arkaly görkezmek üçin


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)
    inlines = [AddressInline]


# CarCategory with inline for subcategories

class CarCategoryInline(admin.TabularInline):
    model = CarCategory
    extra = 1
    fk_name = 'parent'  # Kiçi kategoriýalary parent arkaly görkezmek üçin


@admin.register(CarCategory)
class CarCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)
    inlines = [CarCategoryInline]


# Register other categories and models without inline or changes

admin.site.register(ElinCategory)
admin.site.register(LogistCategory)
admin.site.register(ServiceCategory)
admin.site.register(NewsCategory)
admin.site.register(OtherCategory)
admin.site.register(UserProd)
admin.site.register(ImageTop)


# Customize admin site headers

admin.site.site_title = 'Seýir Admin Panel'
admin.site.site_header = 'Seýir Administration'
admin.site.index_title = 'Seýir Admin Panel'
