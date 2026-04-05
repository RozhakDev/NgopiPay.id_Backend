from rest_framework import viewsets, permissions, mixins
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from .models import Order
from .serializers import OrderReadSerializer, AdminOrderUpdateSerializer

@extend_schema_view(
    list=extend_schema(
        summary="Daftar Pesanan (Admin)",
        description="Melihat semua pesanan masuk. Bisa difilter berdasarkan status (comma-separated).",
        parameters=[
            OpenApiParameter("status", type=str, description="Filter status (contoh: paid,cooking)"),
        ],
        tags=["Admin - Pesanan"]
    ),
    retrieve=extend_schema(
        summary="Detail Pesanan (Admin)",
        description="Melihat detail item dan informasi pelanggan dalam satu pesanan.",
        tags=["Admin - Pesanan"]
    ),
    update=extend_schema(
        summary="Update Status Pesanan (Admin)",
        description="Memperbarui status pesanan (contoh: dari paid ke cooking).",
        tags=["Admin - Pesanan"]
    ),
    partial_update=extend_schema(
        summary="Update Status Pesanan Sebagian (Admin)",
        description="Memperbarui status pesanan secara parsial.",
        tags=["Admin - Pesanan"]
    ),
)
class AdminOrderViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    Pusat kendali pesanan untuk pihak internal (Kasir/Dapur).

    Menyediakan fitur untuk memantau pesanan yang masuk, melihat detail
    pesanan, serta memperbarui status proses (cooking, done).
    """
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        """
        Menyaring data pesanan berdasarkan filter status jika tersedia.
        """
        queryset = Order.objects.prefetch_related('items__menu').order_by('created_at')

        status_param = self.request.query_params.get('status')
        if status_param:
            statuses = [s.strip() for s in status_param.split(',')]
            queryset = queryset.filter(status__in=statuses)

        return queryset
    
    def get_serializer_class(self):
        """
        Menentukan serializer yang tepat untuk pembacaan atau pembaruan status.
        """
        if self.action in ['update', 'partial_update']:
            return AdminOrderUpdateSerializer
        
        return OrderReadSerializer