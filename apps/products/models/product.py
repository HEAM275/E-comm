from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models import AuditableMixins
from apps.products.models.category import Category

STATUS_CHOICES = [
    ("active", _("Active")),
    ("inactive", _("Inactive")),
    ("out of stock", _("Out of Stock")),
]


class Product(AuditableMixins, models.Model):
    name = models.CharField(
        verbose_name=_("Name"), max_length=255, blank=False, null=False
    )
    description = models.TextField(verbose_name=_("Description"), blank=True, null=True)
    price = models.DecimalField(
        verbose_name=_("Price"),
        max_digits=10,
        decimal_places=2,
        blank=False,
        null=False,
    )
    status = models.CharField(
        verbose_name=_("Status"),
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name=_(" Category"),
    )
    stock = models.IntegerField(
        verbose_name=_("Stock"), blank=False, null=False, default=0
    )
    image = models.ImageField(
        upload_to="products", verbose_name=_("image"), blank=True, null=True
    )
    is_active = models.BooleanField(verbose_name=_(("is active")), default=True)

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self):
        return f" Product {self.name} priced at {self.price}"
