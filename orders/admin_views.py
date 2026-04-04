from rest_framework import viewsets, permissions, mixins
from .models import Order
from .serializers import OrderReadSerializer, AdminOrderUpdateSerializer

class AdminOrderViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = Order.objects.prefetch_related('items__menu').order_by('created_at')

        status_param = self.request.query_params.get('status')
        if status_param:
            statuses = [s.strip() for s in status_param.split(',')]
            queryset = queryset.filter(status__in=statuses)

        return queryset
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return AdminOrderUpdateSerializer
        
        return OrderReadSerializer