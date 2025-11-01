from rest_framework import serializers
from .models import Order
from .models import Cart, CartItem
from decimal import Decimal
from products.models import Product


class OrderSerializer(serializers.ModelSerializer):
    # expose the user id as read-only
    user = serializers.ReadOnlyField(source='user.id')

    class Meta:
        model = Order
        fields = ('id', 'user', 'items', 'total', 'status', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at', 'user')

    def validate_items(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError('items must be a list')
        return value


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ('id', 'product_id', 'quantity', 'unit_price')
        read_only_fields = ('unit_price',)


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'user', 'items', 'total', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')

    def get_total(self, obj):
        return str(obj.total())


class AddCartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, data):
        # check product exists
        try:
            Product.objects.get(id=data['product_id'])
        except Product.DoesNotExist:
            raise serializers.ValidationError('Product does not exist')
        return data


class CheckoutSerializer(serializers.Serializer):
    payment_method = serializers.ChoiceField(choices=['card', 'mock'])


class PaymentSerializer(serializers.Serializer):
    method = serializers.ChoiceField(choices=['card', 'mock'])
    card = serializers.DictField(required=False)
