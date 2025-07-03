# apps/payment/admin.py

from django.contrib import admin
from apps.payment.models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "is_paid", "created_by", "created_date")
    list_filter = ("is_paid", "created_date")
    search_fields = ("user__email",)
    readonly_fields = ("created_by", "created_date", "updated_by", "updated_date")

    fieldsets = (
        (None, {"fields": ("user", "is_paid")}),
        (
            "Auditoría",
            {
                "fields": ("created_by", "created_date", "updated_by", "updated_date"),
                "classes": ("collapse",),
            },
        ),
    )

    ordering = ("-created_date",)

    def get_user_email(self, obj):
        return obj.user.email if obj.user else "-"

    get_user_email.short_description = "Usuario"

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user.username
        else:
            obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)
