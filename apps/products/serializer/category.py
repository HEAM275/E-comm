from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.common.serializer import AuditableSerializerMixin
from apps.products.models.category import Category


class CategoryListSerializer(AuditableSerializerMixin):
    class Meta:
        model = Category
        fields = ['name', 'description', 'created_date', 'created_by',
                  'updated_date', 'updated_by', 'deleted_date', 'deleted_by']
        read_only_fields = fields


class CategoryDetailSerializer(AuditableSerializerMixin):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = fields


class CategoryCreateSerializer(AuditableSerializerMixin):
    class Meta:
        model = Category
        fields = ['name', 'description']

    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError(
                _('You must provide a name for this Category'))

        if Category.objects.filter(name=value).exists():
            raise serializers.ValidationError(
                _('Category name already exists'))

        if len(value) > 255:
            raise serializers.ValidationError(
                _('Category name must be less than 255 characters'))

        return value


class CategoryUpdateSerializer(AuditableSerializerMixin):
    class Meta:
        model = Category
        fields = ['name', 'description']
        read_only_fields = ['created_date', 'created_by', 'updated_date', 'updated_by',
                            'deleted_date', 'deleted_by']

    def validate_name(self, value):
        instance = self.instance  # Aquí está el registro actual que se está actualizando

        if not value:
            raise serializers.ValidationError(
                _('You must provide a name for this Category'))

        if len(value) > 255:
            raise serializers.ValidationError(
                _('Category name must be less than 255 characters'))

        # Verifica duplicados EXCLUYENDO la instancia actual
        if Category.objects.filter(name=value).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError(
                _('Category name already exists'))

        return value
