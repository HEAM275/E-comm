from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from apps.products.models.category import Category
from apps.products.models.product import Product


@admin.register(Category)
class CategoryProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'description_short', 'is_active',
                    'created_date', 'updated_date')
    list_filter = ('is_active', 'created_date')
    search_fields = ('name', 'description')
    # Puedes ajustarlo si tienes un campo slug
    prepopulated_fields = {'name': ('name',)}
    readonly_fields = ('created_date', 'created_by', 'updated_date',
                       'updated_by', 'deleted_date', 'deleted_by')
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'description', 'is_active')
        }),
        (_('Audit Information'), {
            'fields': ('created_date', 'created_by', 'updated_date', 'updated_by', 'deleted_date', 'deleted_by'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('name',)

    def description_short(self, obj):
        return obj.description[:50] + '...' if obj.description and len(obj.description) > 50 else obj.description
    description_short.short_description = _('Description')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock',
                    'status', 'is_active', 'created_date')
    list_filter = ('is_active', 'status', 'category')
    search_fields = ('name', 'description', 'category_product__name')
    autocomplete_fields = ['category']
    readonly_fields = ('created_date', 'created_by', 'updated_date',
                       'updated_by', 'deleted_date', 'deleted_by')
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'description', 'category', 'image')
        }),
        (_('Pricing & Stock'), {
            'fields': ('price', 'stock')
        }),
        (_('Status'), {
            'fields': ('is_active', 'status')
        }),
        (_('Audit Information'), {
            'fields': ('created_date', 'created_by', 'updated_date', 'updated_by', 'deleted_date', 'deleted_by'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-created_date',)
    actions = ['make_inactive', 'make_active']

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
    make_inactive.short_description = _('Mark selected products as inactive')

    def make_active(self, request, queryset):
        queryset.update(is_active=True)
    make_active.short_description = _('Mark selected products as active')

    def category(self, obj):
        return obj.category_product.name if obj.category_product else '-'
    category.short_description = _('Category')
    category.admin_order_field = 'category_product__name'
