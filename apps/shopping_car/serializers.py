# apps/shopping_cart/serializers.py
from django.utils.translation import gettext_lazy as _
from apps.products.models.product import Product
from rest_framework import serializers
from apps.products.serializer.product import ProductListSerializer
from .models import CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product"
    )

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_id", "quantity"]
        read_only_fields = ["product"]

    def validate_product_id(self, value):
        if not value.is_active:
            raise serializers.ValidationError(_("Producto no disponible"))
        return value
