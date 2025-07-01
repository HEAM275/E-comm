# apps/payment/viewsets.py
from django.http import Http404
from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import NotFound
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from apps.payment.models import Order
from apps.payment.serializers.order import OrderSerializer
from apps.common.views import BaseModelViewSet  # Tu vista base personalizada

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi as oa


class OrderViewSet(BaseModelViewSet):
    """
    API endpoint for managing orders.
    Only admins can view or modify orders.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # Todos los métodos requieren autenticación de admin por defecto
    permission_classes = [IsAdminUser]

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update', 'partial_update']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound(_("Order not found"))

    @swagger_auto_schema(
        operation_description=_("List all active orders"),
        manual_parameters=[
            oa.Parameter(
                name='Authorization',
                in_=oa.IN_HEADER,
                description="Bearer <access_token>",
                type=oa.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: oa.Response(description=_('List of orders'), schema=OrderSerializer(many=True)),
            403: oa.Response(description=_('Forbidden'), schema=oa.Schema(type=oa.TYPE_OBJECT, properties={'detail': oa.Schema(type=oa.TYPE_STRING)})),
            404: oa.Response(description=_('Not found'), schema=oa.Schema(type=oa.TYPE_OBJECT, properties={'detail': oa.Schema(type=oa.TYPE_STRING)})),
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description=_("Retrieve details of a specific order"),
        manual_parameters=[
            oa.Parameter(
                name='Authorization',
                in_=oa.IN_HEADER,
                description="Bearer <access_token>",
                type=oa.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: oa.Response(description=_('Order details'), schema=OrderSerializer),
            403: oa.Response(description=_('Forbidden'), schema=oa.Schema(type=oa.TYPE_OBJECT, properties={'detail': oa.Schema(type=oa.TYPE_STRING)})),
            404: oa.Response(description=_('Order not found'), schema=oa.Schema(type=oa.TYPE_OBJECT, properties={'detail': oa.Schema(type=oa.TYPE_STRING)})),
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description=_("Create a new order"),
        manual_parameters=[
            oa.Parameter(
                name='Authorization',
                in_=oa.IN_HEADER,
                description="Bearer <access_token>",
                type=oa.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            201: oa.Response(description=_('Order created successfully'), schema=OrderSerializer),
            400: oa.Response(description=_('Validation error'), schema=oa.Schema(type=oa.TYPE_OBJECT, properties={'detail': oa.Schema(type=oa.TYPE_STRING)})),
            403: oa.Response(description=_('Forbidden'), schema=oa.Schema(type=oa.TYPE_OBJECT, properties={'detail': oa.Schema(type=oa.TYPE_STRING)})),
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description=_("Update an existing order"),
        manual_parameters=[
            oa.Parameter(
                name='Authorization',
                in_=oa.IN_HEADER,
                description="Bearer <access_token>",
                type=oa.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: oa.Response(description=_('Order updated successfully'), schema=OrderSerializer),
            400: oa.Response(description=_('Validation error'), schema=oa.Schema(type=oa.TYPE_OBJECT, properties={'detail': oa.Schema(type=oa.TYPE_STRING)})),
            403: oa.Response(description=_('Forbidden'), schema=oa.Schema(type=oa.TYPE_OBJECT, properties={'detail': oa.Schema(type=oa.TYPE_STRING)})),
            404: oa.Response(description=_('Order not found'), schema=oa.Schema(type=oa.TYPE_OBJECT, properties={'detail': oa.Schema(type=oa.TYPE_STRING)})),
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description=_("Partially update an existing order"),
        manual_parameters=[
            oa.Parameter(
                name='Authorization',
                in_=oa.IN_HEADER,
                description="Bearer <access_token>",
                type=oa.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: oa.Response(description=_('Order updated successfully'), schema=OrderSerializer),
            400: oa.Response(description=_('Validation error'), schema=oa.Schema(type=oa.TYPE_OBJECT, properties={'detail': oa.Schema(type=oa.TYPE_STRING)})),
            403: oa.Response(description=_('Forbidden'), schema=oa.Schema(type=oa.TYPE_OBJECT, properties={'detail': oa.Schema(type=oa.TYPE_STRING)})),
            404: oa.Response(description=_('Order not found'), schema=oa.Schema(type=oa.TYPE_OBJECT, properties={'detail': oa.Schema(type=oa.TYPE_STRING)})),
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description=_("Delete an order (soft delete)"),
        manual_parameters=[
            oa.Parameter(
                name='Authorization',
                in_=oa.IN_HEADER,
                description="Bearer <access_token>",
                type=oa.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            204: oa.Response(description=_('Order successfully deleted')),
            403: oa.Response(description=_('Forbidden'), schema=oa.Schema(type=oa.TYPE_OBJECT, properties={'detail': oa.Schema(type=oa.TYPE_STRING)})),
            404: oa.Response(description=_('Order not found'), schema=oa.Schema(type=oa.TYPE_OBJECT, properties={'detail': oa.Schema(type=oa.TYPE_STRING)})),
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
