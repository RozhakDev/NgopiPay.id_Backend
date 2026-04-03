from rest_framework import serializers
from django.db import transaction
from .models import Order, OrderItem
from menus.models import Menu
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
        return f"https://paymenku.com/dummy-pay/{obj.reference_id}"
    

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

        return order
    
    def to_representation(self, instance):
        return OrderReadSerializer(instance).data