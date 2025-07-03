# apps/shopping_cart/admin.py

from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1
    readonly_fields = ("added_at",)
    autocomplete_fields = ["product"]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]
    list_display = ("id", "user", "get_total_items")
    search_fields = ("user__email",)
    readonly_fields = ("created_at", "updated_at")

    def get_total_items(self, obj):
        return obj.items.count()

    get_total_items.short_description = "Número de ítems"
