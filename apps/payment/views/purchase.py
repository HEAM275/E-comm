# apps/payment/views.py
from django.utils.translation import gettext_lazy as _

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.payment.serializers.purchase import PurchaseRequestSerializer
from apps.payment.serializers.order import OrderSerializer
from apps.payment.models import Order, OrderItem

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi as oa

# views.py


class PurchaseView(APIView):

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description=_(
            "Process a purchase with one or more products"),
        manual_parameters=[
            oa.Parameter(
                name='Authorization',
                in_=oa.IN_HEADER,
                description="Bearer <access_token>",
                type=oa.TYPE_STRING,
                required=True,
            ),
        ],
        request_body=PurchaseRequestSerializer,
        responses={
            201: oa.Response(_('Purchase successful')),
            400: oa.Response(_('Validation failed'))
        }
    )
    def post(self, request):
        serializer = PurchaseRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        validated_items = validated_data["validated_items"]
        total_price = validated_data["total_price"]
        payment_amount = validated_data["payment_amount"]
        is_partial = validated_data["is_partial"]
        message = validated_data.get("partial_message", "")

        # Crear orden con el serializador (llama a perform_create())
        order_serializer = OrderSerializer(data={"user": request.user.id})
        order_serializer.is_valid(raise_exception=True)
        # Aquí se usará BaseModelViewSet
        order = order_serializer.save(is_paid=True)
        self.perform_create(order_serializer)

        successful_items = []
        remaining_payment = payment_amount

        for item in validated_items:
            total_cost = item["quantity"] * item["price"]

            if remaining_payment >= total_cost:
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    quantity=item["quantity"],
                    price=item["price"]
                )
                successful_items.append({
                    "product": item["product"].name,
                    "quantity": item["quantity"]
                })
                remaining_payment -= total_cost

                product = item["product"]
                product.stock -= item["quantity"]
                if product.stock == 0:
                    product.is_active = False
                product.save()
            else:
                max_quantity = int(remaining_payment // item["price"])
                if max_quantity > 0:
                    OrderItem.objects.create(
                        order=order,
                        product=item["product"],
                        quantity=max_quantity,
                        price=item["price"]
                    )
                    successful_items.append({
                        "product": item["product"].name,
                        "quantity": max_quantity
                    })
                    remaining_payment -= max_quantity * item["price"]

                    product = item["product"]
                    product.stock -= max_quantity
                    if product.stock == 0:
                        product.is_active = False
                    product.save()

        response_data = {
            "message": "Compra realizada con éxito (parcial)" if is_partial else "Compra realizada con éxito",
            "successful_items": successful_items,
            "total": float(total_price),
            "paid": float(payment_amount),
            "change": float(remaining_payment),
        }

        if is_partial and message:
            response_data["note"] = message

        return Response(response_data, status=status.HTTP_201_CREATED)
