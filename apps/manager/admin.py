from django.contrib import admin
from django.utils import timezone
from apps.common.utils import get_user_fullname
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("email", "first_name", "last_name", "is_staff", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (("Información Personal"), {"fields": ("first_name", "last_name")}),
        (
            ("Permisos"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (("Fechas importantes"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
        (("Información Personal"), {"fields": ("first_name", "last_name")}),
        (("Permisos"), {"fields": ("is_active", "is_staff", "is_superuser")}),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Si es una creación
            if request.user.is_authenticated:
                obj.created_by = get_user_fullname(request.user)
                obj.created_date = timezone.now()
        else:  # Si es una actualización
            if request.user.is_authenticated:
                obj.updated_by = get_user_fullname(request.user)
                obj.updated_date = timezone.now()

        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        if request.user.is_authenticated:
            obj.deleted_by = get_user_fullname(request.user)
            obj.deleted_date = timezone.now()
            obj.is_active = False
            obj.save()
        else:
            obj.is_active = False
            obj.deleted_by = "Anónimo"
            obj.deleted_date = timezone.now()
            obj.save()
