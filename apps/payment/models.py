# apps/payment/models.py

from django.db import models
from apps.common.models import AuditableMixins
from apps.manager.models import User
from apps.products.models.product import Product


class Order(AuditableMixins):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Orden {self.id} - {self.user.email}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
