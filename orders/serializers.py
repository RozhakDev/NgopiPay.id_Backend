from rest_framework import serializers
from django.db import transaction
from .models import Order, OrderItem
from menus.models import Menu
from payments.models import Payment
from payments.services import PaymenkuService
from .utils import generate_reference_id

class OrderItemReadSerializer(serializers.ModelSerializer):
    menu_name = serializers.CharField(source='menu.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'menu_name', 'quantity', 'price', 'subtotal']


class OrderReadSerializer(serializers.ModelSerializer):
    items = OrderItemReadSerializer(many=True, read_only=True)
    pay_url = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'reference_id', 'customer_name', 'table_number', 'status', 'total_price', 'pay_url', 'items', 'created_at']

    def get_pay_url(self, obj):
        if hasattr(obj, 'payment') and obj.payment.pay_url:
            return obj.payment.pay_url
        return None
    

class OrderItemCreateSerializer(serializers.Serializer):
    menu_id = serializers.PrimaryKeyRelatedField(
        queryset=Menu.objects.filter(is_available=True), 
        source='menu'
    )
    quantity = serializers.IntegerField(min_value=1)

class OrderCreateSerializer(serializers.Serializer):
    customer_name = serializers.CharField(max_length=100)
    table_number = serializers.IntegerField(min_value=1)
    items = OrderItemCreateSerializer(many=True, allow_empty=False)

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')

        order = Order.objects.create(
            reference_id=generate_reference_id(),
            customer_name=validated_data['customer_name'],
            table_number=validated_data['table_number'],
            status='pending_payment'
        )

        total_price = 0

        for item in items_data:
            menu = item['menu']
            quantity = item['quantity']
            price = menu.price

            OrderItem.objects.create(
                order=order,
                menu=menu,
                quantity=quantity,
                price=price
            )

            total_price += (price * quantity)

        order.total_price = total_price
        order.save()

        payment_result = PaymenkuService.create_transaction(
            reference_id=order.reference_id,
            amount=order.total_price,
            customer_name=order.customer_name
        )

        pay_url = None
        trx_id = None
        if payment_result.get('success'):
            pay_url = payment_result.get('pay_url')
            trx_id = payment_result.get('trx_id')

        Payment.objects.create(
            order=order,
            reference_id=order.reference_id,
            trx_id=trx_id,
            amount=order.total_price,
            payment_channel='qris',
            pay_url=pay_url
        )

        return order
    
    def to_representation(self, instance):
        return OrderReadSerializer(instance).data
    

class AdminOrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

    def validate_status(self, value):
        allowed_statuses = ['paid', 'cooking', 'done', 'cancelled']
        if value not in allowed_statuses:
            raise serializers.ValidationError(f"Status '{value}' tidak diizinkan untuk diubah secara manual.")
        return value