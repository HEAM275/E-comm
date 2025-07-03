from django.utils.translation import gettext_lazy as _

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.shortcuts import get_object_or_404

from apps.payment.models import Order, OrderItem
from apps.payment.serializers.order import OrderSerializer
from apps.payment.serializers.purchase import PurchaseRequestSerializer
from apps.manager.models import User

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi as oa


def get_user_fullname(user):
    if not user.is_authenticated:
        return None
    full_name = f"{user.first_name} {user.last_name}".strip()
    return full_name or user.username


# Definición común del header de autorización
AUTH_HEADER = [
    oa.Parameter(
        name="Authorization",
        in_=oa.IN_HEADER,
        description="Bearer <access_token>",
        type=oa.TYPE_STRING,
        required=True,
    )
]


class PurchaseView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description=_("Crear una nueva orden de compra"),
        manual_parameters=AUTH_HEADER,
        request_body=PurchaseRequestSerializer,
        responses={
            201: oa.Response(description=_("Compra realizada con éxito")),
            400: oa.Response(
                description=_("Error de validación"),
                schema=oa.Schema(
                    type=oa.TYPE_OBJECT,
                    properties={"detail": oa.Schema(type=oa.TYPE_STRING)},
                ),
            ),
            403: oa.Response(
                description=_("Permiso denegado"),
                schema=oa.Schema(
                    type=oa.TYPE_OBJECT,
                    properties={"detail": oa.Schema(type=oa.TYPE_STRING)},
                ),
            ),
        },
    )
    def post(self, request):
        """Crear una nueva orden"""
        serializer = PurchaseRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        validated_items = validated_data["validated_items"]
        total_price = validated_data["total_price"]
        payment_amount = validated_data["payment_amount"]

        # Crear la orden
        full_name = get_user_fullname(request.user)
        if not full_name:
            raise PermissionDenied("Usuario no autenticado")

        order = Order.objects.create(
            user=request.user,
            is_paid=True,
            created_by=full_name,
            created_date=timezone.now(),
        )

        successful_items = []
        remaining_payment = payment_amount

        for item in validated_items:
            total_cost = item["quantity"] * item["price"]

            if remaining_payment >= total_cost:
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    quantity=item["quantity"],
                    price=item["price"],
                )
                successful_items.append(
                    {"product": item["product"].name, "quantity": item["quantity"]}
                )
                remaining_payment -= total_cost

                # Actualizar stock
                product = item["product"]
                product.stock -= item["quantity"]
                if product.stock == 0:
                    product.is_active = False
                product.save()

        # Guardar updated_by y updated_date (opcional)
        order.updated_by = full_name
        order.updated_date = timezone.now()
        order.save(update_fields=["updated_by", "updated_date"])

        return Response(
            {
                "message": "Compra realizada con éxito",
                "successful_items": successful_items,
                "total": float(total_price),
                "paid": float(payment_amount),
                "change": float(remaining_payment),
            },
            status=status.HTTP_201_CREATED,
        )

    @swagger_auto_schema(
        operation_description=_("Obtener detalles de una orden por ID"),
        manual_parameters=AUTH_HEADER,
        responses={
            200: oa.Response(
                description=_("Detalles de la orden"), schema=OrderSerializer
            ),
            400: oa.Response(
                description=_("ID requerido"),
                schema=oa.Schema(
                    type=oa.TYPE_OBJECT,
                    properties={"error": oa.Schema(type=oa.TYPE_STRING)},
                ),
            ),
            404: oa.Response(
                description=_("Orden no encontrada"),
                schema=oa.Schema(
                    type=oa.TYPE_OBJECT,
                    properties={"error": oa.Schema(type=oa.TYPE_STRING)},
                ),
            ),
        },
    )
    def get(self, request, pk=None):
        """Obtener detalles de una orden específica"""
        if pk:
            order = get_object_or_404(Order, id=pk, user=request.user)
            return Response(
                {
                    "id": order.id,
                    "user": order.user.email,
                    "is_paid": order.is_paid,
                    "created_by": order.created_by,
                    "created_date": order.created_date,
                    "updated_by": order.updated_by,
                    "updated_date": order.updated_date,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"error": "No se proporcionó un ID de orden"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @swagger_auto_schema(
        operation_description=_("Actualizar completamente una orden"),
        manual_parameters=AUTH_HEADER,
        request_body=oa.Schema(
            type=oa.TYPE_OBJECT,
            properties={
                "is_paid": oa.Schema(type=oa.TYPE_BOOLEAN, description="Estado de pago")
            },
            required=["is_paid"],
        ),
        responses={
            200: oa.Response(description=_("Orden actualizada exitosamente")),
            400: oa.Response(description=_("Datos inválidos o ID requerido")),
            404: oa.Response(description=_("Orden no encontrada")),
        },
    )
    def put(self, request, pk=None):
        """Actualizar completamente una orden"""
        if not pk:
            return Response(
                {"error": "ID requerido"}, status=status.HTTP_400_BAD_REQUEST
            )

        order = get_object_or_404(Order, id=pk, user=request.user)

        full_name = get_user_fullname(request.user)
        if not full_name:
            raise PermissionDenied("Usuario no autenticado")

        # Aquí puedes validar datos de entrada si necesitas actualizar items
        # Ejemplo básico: actualizar campo is_paid
        order.is_paid = request.data.get("is_paid", order.is_paid)
        order.updated_by = full_name
        order.updated_date = timezone.now()
        order.save(update_fields=["is_paid", "updated_by", "updated_date"])

        return Response(
            {
                "message": "Orden actualizada exitosamente",
                "is_paid": order.is_paid,
                "updated_by": order.updated_by,
                "updated_date": order.updated_date,
            },
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_description=_(
            "Actualizar parcialmente una orden (por ejemplo, cambiar estado de pago)"
        ),
        manual_parameters=AUTH_HEADER,
        request_body=oa.Schema(
            type=oa.TYPE_OBJECT,
            properties={
                "is_paid": oa.Schema(
                    type=oa.TYPE_BOOLEAN, description="Nuevo estado de pago"
                )
            },
        ),
        responses={
            200: oa.Response(description=_("Orden actualizada parcialmente")),
            400: oa.Response(description=_("Datos inválidos o ID requerido")),
            404: oa.Response(description=_("Orden no encontrada")),
        },
    )
    def patch(self, request, pk=None):
        """Actualización parcial de una orden"""
        if not pk:
            return Response(
                {"error": "ID requerido"}, status=status.HTTP_400_BAD_REQUEST
            )

        order = get_object_or_404(Order, id=pk, user=request.user)

        full_name = get_user_fullname(request.user)
        if not full_name:
            raise PermissionDenied("Usuario no autenticado")

        # Solo actualizamos algunos campos
        if "is_paid" in request.data:
            order.is_paid = request.data["is_paid"]

        order.updated_by = full_name
        order.updated_date = timezone.now()
        order.save(update_fields=["is_paid", "updated_by", "updated_date"])

        return Response(
            {
                "message": "Orden actualizada parcialmente",
                "is_paid": order.is_paid,
                "updated_by": order.updated_by,
                "updated_date": order.updated_date,
            },
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_description=_("Eliminar una orden (soft-delete)"),
        manual_parameters=AUTH_HEADER,
        responses={
            204: oa.Response(description=_("Orden eliminada exitosamente")),
            400: oa.Response(description=_("ID requerido")),
            404: oa.Response(description=_("Orden no encontrada")),
        },
    )
    def delete(self, request, pk=None):
        """Eliminar una orden (soft-delete)"""
        if not pk:
            return Response(
                {"error": "ID requerido"}, status=status.HTTP_400_BAD_REQUEST
            )

        order = get_object_or_404(Order, id=pk, user=request.user)

        full_name = get_user_fullname(request.user)
        if not full_name:
            raise PermissionDenied("Usuario no autenticado")

        # Soft-delete
        order.deleted_by = full_name
        order.deleted_date = timezone.now()
        order.is_active = False
        order.save(update_fields=["deleted_by", "deleted_date", "is_active"])

        return Response(
            {"message": "Orden eliminada exitosamente"},
            status=status.HTTP_204_NO_CONTENT,
        )
