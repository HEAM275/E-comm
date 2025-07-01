# apps/payment/serializers.py

from rest_framework import serializers
from apps.products.models.product import Product


class PurchaseItemSerializer(serializers.Serializer):
    product_name = serializers.CharField(max_length=255)
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, data):
        product_name = data['product_name']
        quantity = data['quantity']

        try:
            product = Product.objects.get(name__iexact=product_name)
        except Product.DoesNotExist:
            raise serializers.ValidationError({
                "product_name": f"No se encontró ningún producto con el nombre '{product_name}'"
            })

        if not product.is_active:
            raise serializers.ValidationError({
                "product_name": f"El producto '{product.name}' no está disponible"
            })

        if product.stock < quantity:
            raise serializers.ValidationError({
                "quantity": f"No hay suficiente stock de '{product.name}'. Disponible: {product.stock}, solicitado: {quantity}"
            })

        # Añadimos el producto al validated_data para usarlo luego
        data['product'] = product
        return data


class PurchaseRequestSerializer(serializers.Serializer):
    items = PurchaseItemSerializer(many=True)
    payment_amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate(self, data):
        validated_items = []
        partial_purchase = False
        partial_message = ""

        items = data.get('items', [])
        payment_amount = data['payment_amount']

        for item in items:
            try:
                # Validación normal
                item_serializer = PurchaseItemSerializer(data=item)
                item_serializer.is_valid(raise_exception=True)
            except serializers.ValidationError as e:
                detail = e.detail
                if 'product_name' in detail:
                    # Si falla por nombre de producto, propagamos el error
                    raise serializers.ValidationError(detail)
                elif 'quantity' in detail:
                    # Si falla por stock, intentamos validar cantidad menor
                    product = item_serializer.validated_data.get('product')
                    if product:
                        max_possible = min(product.stock, item['quantity'])
                        partial_message += f"Solo puedes comprar {max_possible} de '{product.name}'. "
                        validated_items.append({
                            "product": product,
                            "quantity": max_possible,
                            "price": product.price
                        })
                        partial_purchase = True
                    else:
                        raise serializers.ValidationError(detail)
            else:
                validated_item = item_serializer.validated_data
                validated_items.append({
                    "product": validated_item['product'],
                    "quantity": validated_item['quantity'],
                    "price": validated_item['product'].price
                })

        total_price = sum(item["quantity"] * item["price"]
                          for item in validated_items)

        if payment_amount < total_price:
            partial_message += "Monto abonado insuficiente para todos los productos. Se procesará una compra parcial."

        return {
            "validated_items": validated_items,
            "total_price": total_price,
            "payment_amount": payment_amount,
            "partial_message": partial_message.strip(),
            "is_partial": partial_purchase or payment_amount < total_price
        }
