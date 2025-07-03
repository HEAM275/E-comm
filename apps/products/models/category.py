from django.utils.translation import gettext_lazy as _
from django.db import models
from apps.common.models import AuditableMixins


class Category(AuditableMixins):
    name = models.CharField(max_length=255, verbose_name=_("Category name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is active"))

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name
