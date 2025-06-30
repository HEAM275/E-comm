from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.common.serializer import AuditableSerializerMixin
from apps.products.models.product import STATUS_CHOICES, Product


class ProductListSerializer(AuditableSerializerMixin):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category',
                  'stock', 'price', 'image', 'status']


class ProductRetrieveSerializer(AuditableSerializerMixin):
    class Meta:
        model = Product
        fields = '__all__'


class ProductCreateSerializer(AuditableSerializerMixin):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category',
                  'stock', 'price', 'image', 'is_active', 'status']

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError(
                _('Name must be at least 3 characters long.'))
        if len(value) > 255:
            raise serializers.ValidationError(
                _('Name cannot exceed 255 characters.'))
        if Product.objects.filter(name=value).exists():
            raise serializers.ValidationError(
                _('A product with this name already exists.'))
        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                _('Price must be greater than zero.'))
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError(_('Stock cannot be negative.'))
        return value

    def validate_image(self, value):
        if value:
            filesize = value.size
            megabyte_limit = 5.0
            if filesize > megabyte_limit * 1024 * 1024:
                raise serializers.ValidationError(
                    _('Max file size is %sMB' % str(megabyte_limit)))
        return value

    def validate_status(self, value):
        allowed_statuses = [choice[0] for choice in STATUS_CHOICES]
        if value not in allowed_statuses:
            raise serializers.ValidationError(_('Invalid status selected.'))
        return value

    def validate(self, data):
        name = data.get('name')
        category = data.get('category_product')

        if category and Product.objects.filter(name=name, category_product=category).exists():
            raise serializers.ValidationError({
                'name': _('A product with this name already exists in the selected category.')
            })

        return data


class ProductUpdateSerializer(AuditableSerializerMixin):
    class Meta:
        model = Product
        fields = [
            'name',
            'description',
            'category',
            'stock',
            'price',
            'image',
            'is_active',
            'status',
            # Campos de auditoría (deben ser solo lectura)
            'created_date',
            'created_by',
            'updated_date',
            'updated_by',
            'deleted_date',
            'deleted_by',
        ]
        read_only_fields = [
            'created_date',
            'created_by',
            'updated_date',
            'updated_by',
            'deleted_date',
            'deleted_by',
        ]

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError(
                _('Name must be at least 3 characters long.'))
        if len(value) > 255:
            raise serializers.ValidationError(
                _('Name cannot exceed 255 characters.'))

        instance = self.instance  # Producto que se está actualizando
        if Product.objects.filter(name=value).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError(
                _('A product with this name already exists.'))

        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                _('Price must be greater than zero.'))
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError(_('Stock cannot be negative.'))
        return value

    def validate_image(self, value):
        if value:
            filesize = value.size
            megabyte_limit = 5.0
            if filesize > megabyte_limit * 1024 * 1024:
                raise serializers.ValidationError(
                    _('Max file size is %sMB' % str(megabyte_limit)))
        return value

    def validate_status(self, value):
        allowed_statuses = [choice[0] for choice in Product.STATUS_CHOICES]
        if value not in allowed_statuses:
            raise serializers.ValidationError(_('Invalid status selected.'))
        return value

    def validate(self, data):
        name = data.get('name')
        category = data.get('category_product')
        instance = self.instance

        if category and Product.objects.filter(name=name).exclude(pk=instance.pk).filter(category_product=category).exists():
            raise serializers.ValidationError({
                'name': _('A product with this name already exists in the selected category.')
            })

        return data
