from rest_framework import viewsets, mixins, permissions
from .models import Order
from .serializers import OrderCreateSerializer, OrderReadSerializer

class OrderViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Order.objects.all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderReadSerializer