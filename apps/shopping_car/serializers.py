# apps/shopping_cart/serializers.py

from rest_framework import serializers
from apps.products.models.product import Product
from apps.products.serializer.product import ProductListSerializer
from .models import CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product'
    )

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity']
