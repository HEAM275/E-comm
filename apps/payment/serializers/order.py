# serializers.py

from rest_framework import serializers
from apps.payment.models import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['created_date',
                            'created_by', 'updated_date', 'updated_by']
