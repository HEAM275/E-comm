from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.products.models.product import Product
from apps.payment.models import Order, OrderItem
from apps.shopping_car.models import Cart, CartItem
from apps.shopping_car.serializers import CartItemSerializer
from apps.manager.models import User

from drf_yasg import openapi as oa
from drf_yasg.utils import swagger_auto_schema


def get_user_fullname(user):
    if not user.is_authenticated:
        return None
    full_name = f"{user.first_name} {user.last_name}".strip()
    return full_name or user.username


# Definimos parámetros reutilizables para Swagger
AUTH_HEADER = [
    oa.Parameter(
        "Authorization",
        oa.IN_HEADER,
        description="Bearer <access_token>",
        type=oa.TYPE_STRING,
        required=True,
    )
]

CART_ITEM_BODY = oa.Schema(
    type=oa.TYPE_OBJECT,
    properties={
        "product_id": oa.Schema(type=oa.TYPE_INTEGER, description="ID del producto"),
        "quantity": oa.Schema(type=oa.TYPE_INTEGER, default=1),
    },
    required=["product_id"],
)

UPDATE_CART_ITEM_BODY = oa.Schema(
    type=oa.TYPE_OBJECT,
    properties={
        "item_id": oa.Schema(
            type=oa.TYPE_INTEGER, description="ID del ítem en el carrito"
        ),
        "quantity": oa.Schema(type=oa.TYPE_INTEGER, description="Nueva cantidad"),
    },
    required=["item_id"],
)

CLEAR_CART_BODY = oa.Schema(type=oa.TYPE_OBJECT, properties={})

CHECKOUT_CART_BODY = oa.Schema(
    type=oa.TYPE_OBJECT,
    properties={"payment_amount": oa.Schema(type=oa.TYPE_NUMBER)},
    required=["payment_amount"],
)


class ShoppingCartView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description=_("Agregar un producto al carrito"),
        manual_parameters=AUTH_HEADER,
        request_body=CART_ITEM_BODY,
        responses={
            201: oa.Response(description=_("Producto agregado al carrito")),
            404: oa.Response(description=_("Producto no encontrado")),
        },
    )
    def post(self, request):
        """Agregar producto al carrito"""
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": _("Producto no encontrado")}, status=status.HTTP_404_NOT_FOUND
            )

        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity

        # Validar stock
        if product.stock < cart_item.quantity:
            return Response(
                {
                    "error": _("Stock insuficiente. Disponible: %(stock)s")
                    % {"stock": product.stock}
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description=_("Ver contenido del carrito"),
        manual_parameters=AUTH_HEADER,
        responses={
            200: oa.Response(
                description=_("Contenido del carrito"),
                schema=CartItemSerializer(many=True),
            ),
            404: oa.Response(description=_("Carrito vacío o inexistente")),
        },
    )
    def get(self, request):
        """Ver contenido del carrito"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        items = cart.items.all()
        if not items:
            return Response(
                {"message": _("Tu carrito está vacío")}, status=status.HTTP_200_OK
            )
        serializer = CartItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description=_("Actualizar cantidad de un producto en el carrito"),
        manual_parameters=AUTH_HEADER,
        request_body=UPDATE_CART_ITEM_BODY,
        responses={
            200: oa.Response(description=_("Cantidad actualizada")),
            404: oa.Response(description=_("Ítem no encontrado")),
        },
    )
    def put(self, request):
        """Actualizar cantidad de un producto en el carrito"""
        item_id = request.data.get("item_id")
        quantity = request.data.get("quantity")

        if not item_id or not item_id.isdigit():
            return Response(
                {"error": _("ID inválido o no proporcionado")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        item_id = int(item_id)

        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response(
                {"error": _("Ítem no encontrado en tu carrito")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if quantity and int(quantity) > 0:
            if cart_item.product.stock < int(quantity):
                return Response(
                    {
                        "error": _(
                            "No hay suficiente stock de %(product)s. Disponible: %(stock)s"
                        )
                        % {
                            "product": cart_item.product.name,
                            "stock": cart_item.product.stock,
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            cart_item.quantity = int(quantity)
            cart_item.save()
        else:
            cart_item.delete()
            return Response(
                {"message": _("Producto eliminado del carrito")},
                status=status.HTTP_204_NO_CONTENT,
            )

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description=_("Eliminar un producto específico del carrito"),
        manual_parameters=AUTH_HEADER,
        request_body=oa.Schema(
            type=oa.TYPE_OBJECT, properties={"item_id": oa.Schema(type=oa.TYPE_INTEGER)}
        ),
        responses={
            204: oa.Response(description=_("Producto eliminado del carrito")),
            404: oa.Response(description=_("Ítem no encontrado")),
        },
    )
    def delete(self, request):
        """Eliminar un ítem del carrito"""
        item_id = request.data.get("item_id")

        if not item_id or not item_id.isdigit():
            return Response(
                {"error": _("ID inválido o no proporcionado")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        item_id = int(item_id)

        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response(
                {"error": _("Ítem no encontrado en tu carrito")},
                status=status.HTTP_404_NOT_FOUND,
            )

        cart_item.delete()
        return Response(
            {"message": _("Producto eliminado del carrito")},
            status=status.HTTP_204_NO_CONTENT,
        )


class ClearCartView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description=_("Vaciar todo el carrito"),
        manual_parameters=AUTH_HEADER,
        responses={
            200: oa.Response(description=_("Carrito vaciado correctamente")),
            404: oa.Response(description=_("Carrito no encontrado")),
        },
    )
    def post(self, request):
        """Vaciar todo el carrito"""
        try:
            cart = Cart.objects.get(user=request.user)
            cart.items.all().delete()
            return Response(
                {"message": _("Carrito vaciado correctamente")},
                status=status.HTTP_200_OK,
            )
        except Cart.DoesNotExist:
            return Response(
                {"error": _("No tienes un carrito")}, status=status.HTTP_404_NOT_FOUND
            )


class CheckoutFromCartView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description=_("Realizar compra desde el carrito"),
        manual_parameters=AUTH_HEADER,
        request_body=CHECKOUT_CART_BODY,
        responses={
            201: oa.Response(description=_("Compra realizada con éxito")),
            400: oa.Response(description=_("Monto insuficiente o carrito vacío")),
            404: oa.Response(description=_("Producto sin stock")),
        },
    )
    def post(self, request):
        """Realizar compra desde el carrito"""
        payment_amount = float(request.data.get("payment_amount", 0.0))
        cart = Cart.objects.filter(user=request.user).first()

        if not cart or not cart.items.exists():
            return Response(
                {"error": _("Tu carrito está vacío")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        items = cart.items.all()
        total_price = sum(item.product.price * item.quantity for item in items)

        if payment_amount < total_price:
            return Response(
                {
                    "error": _("El monto abonado es insuficiente"),
                    "total": total_price,
                    "paid": payment_amount,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        full_name = get_user_fullname(request.user)
        if not full_name:
            raise PermissionDenied(_("Usuario no autenticado"))

        # Crear orden
        order = Order.objects.create(
            user=request.user,
            is_paid=True,
            created_by=full_name,
            created_date=timezone.now(),
        )

        successful_items = []
        remaining_payment = payment_amount

        for item in items:
            product = item.product
            quantity = item.quantity
            price = product.price
            total_cost = quantity * price

            if remaining_payment >= total_cost:
                OrderItem.objects.create(
                    order=order, product=product, quantity=quantity, price=price
                )
                successful_items.append({"product": product.name, "quantity": quantity})
                remaining_payment -= total_cost
                product.stock -= quantity
                if product.stock == 0:
                    product.is_active = False
                product.save()
            else:
                max_quantity = int(remaining_payment // price)
                if max_quantity > 0:
                    OrderItem.objects.create(
                        order=order, product=product, quantity=max_quantity, price=price
                    )
                    successful_items.append(
                        {"product": product.name, "quantity": max_quantity}
                    )
                    remaining_payment -= max_quantity * price
                    product.stock -= max_quantity
                    if product.stock == 0:
                        product.is_active = False
                    product.save()

        # Vaciar carrito después de la compra
        cart.items.all().delete()

        response_data = {
            "message": _("Compra realizada con éxito"),
            "successful_items": successful_items,
            "total": round(total_price, 2),
            "paid": round(payment_amount, 2),
            "change": round(remaining_payment, 2),
        }

        return Response(response_data, status=status.HTTP_201_CREATED)
