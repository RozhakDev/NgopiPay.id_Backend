from rest_framework import viewsets, mixins, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Order
from .serializers import OrderCreateSerializer, OrderReadSerializer

class OrderViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Order.objects.all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderReadSerializer
    
    @action(detail=True, methods=['get'])
    def receipt(self, request, pk=None):
        order = self.get_object()

        if order.status == 'pending_payment':
            return Response(
                {"status": "error", "message": "Pesanan belum dibayar, struk tidak tersedia."},
                status=400
            )
        
        receipt_data = {
            "receipt_info": {
                "date": order.created_at.strftime("%d %b %Y, %H:%M"),
                "customer_name": order.customer_name,
                "location": f"Meja {order.table_number} - NgopiPay.id",
            },
            "items": [
                {
                    "name": item.menu.name,
                    "quantity": item.quantity,
                    "price": item.price,
                    "subtotal": item.subtotal
                } for item in order.items.all()
            ],
            "payment_detail": {
                "trx_id": order.payment.trx_id if hasattr(order, 'payment') else "-",
                "method": order.payment.payment_channel.upper() if hasattr(order, 'payment') and order.payment.payment_channel else "QRIS",
                "total_paid": order.total_price
            }
        }

        return Response({"status": "success", "data": receipt_data})