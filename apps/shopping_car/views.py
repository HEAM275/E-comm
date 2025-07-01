# apps/shopping_cart/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apps.products.models.product import Product
from .models import Cart, CartItem
from .serializers import CartItemSerializer


class ShoppingCartView(APIView):
    permission_classes = [IsAuthenticated]

    def get_cart(self, user):
        cart, created = Cart.objects.get_or_create(user=user)
        return cart

    def post(self, request):
        """Agregar producto al carrito"""
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        cart = self.get_cart(request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product)

        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity

        cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        """Ver contenido del carrito"""
        cart = self.get_cart(request.user)
        items = cart.items.all()
        serializer = CartItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        """Actualizar cantidad de un producto en el carrito"""
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity')

        try:
            cart_item = CartItem.objects.get(
                id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({'error': 'Ítem no encontrado en tu carrito'}, status=status.HTTP_404_NOT_FOUND)

        if quantity and int(quantity) > 0:
            cart_item.quantity = int(quantity)
            cart_item.save()
        else:
            cart_item.delete()
            return Response({'message': 'Producto eliminado del carrito'}, status=status.HTTP_204_NO_CONTENT)

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        """Eliminar un producto del carrito"""
        item_id = request.data.get('item_id')

        try:
            cart_item = CartItem.objects.get(
                id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({'error': 'Ítem no encontrado en tu carrito'}, status=status.HTTP_404_NOT_FOUND)

        cart_item.delete()
        return Response({'message': 'Producto eliminado del carrito'}, status=status.HTTP_204_NO_CONTENT)


class ClearCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Vaciar el carrito"""
        try:
            cart = Cart.objects.get(user=request.user)
            cart.items.all().delete()
            return Response({'message': 'Carrito vaciado correctamente'}, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({'error': 'No tienes un carrito'},
                            status=status.HTTP_404_NOT_FOUND)
