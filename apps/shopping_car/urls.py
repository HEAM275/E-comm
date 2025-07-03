# apps/shopping_cart/urls.py

from django.urls import path
from apps.shopping_car.views import (
    ShoppingCartView,
    ClearCartView,
    CheckoutFromCartView,
)

urlpatterns = [
    path("cart/", ShoppingCartView.as_view(), name="shopping-cart"),
    path("cart/clear/", ClearCartView.as_view(), name="clear-cart"),
    path("cart/checkout/", CheckoutFromCartView.as_view(), name="cart-checkout"),
]
