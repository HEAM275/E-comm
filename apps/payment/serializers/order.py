# serializers.py

from rest_framework import serializers
from apps.common.serializer import AuditableSerializerMixin
from apps.payment.models import Order


class OrderSerializer(AuditableSerializerMixin):
    class Meta:
        model = Order
        fields = "__all__"
        read_only_fields = ["created_date", "created_by", "updated_date", "updated_by"]
