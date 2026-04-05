import logging
from rest_framework import viewsets, mixins, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import Order
from .serializers import OrderCreateSerializer, OrderReadSerializer
from .utils import verify_order_access_token

logger = logging.getLogger(__name__)


class OrderAccessPermission(permissions.BasePermission):
    """
    Mengontrol hak akses pelanggan terhadap data pesanan.

    Memastikan pelanggan hanya dapat melihat pesanan milik sendiri
    menggunakan validasi token akses yang dikirim klien.
    """
    message = "Token akses order tidak valid."

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        """
        Memvalidasi kepemilikan objek pesanan berdasarkan token.
        """
        if view.action == 'create':
            return True

        if view.action not in {'retrieve', 'receipt'}:
            return True

        token = request.query_params.get('token') or request.headers.get('X-Order-Token')
        if not token:
            logger.warning(
                "Akses order ditolak karena token tidak tersedia. reference_id=%s",
                getattr(obj, 'reference_id', None),
            )
            return False

        is_valid = verify_order_access_token(obj, token)
        if not is_valid:
            logger.warning(
                "Akses order ditolak karena token tidak valid. reference_id=%s",
                getattr(obj, 'reference_id', None),
            )
        return is_valid

@extend_schema_view(
    create=extend_schema(
        summary="Buat Pesanan Baru",
        description="Melakukan checkout pesanan. Mengembalikan URL pembayaran Paymenku.",
        tags=["Pesanan"]
    ),
    retrieve=extend_schema(
        summary="Cek Status Pesanan",
        description="Melihat status pesanan pelanggan. Memerlukan Token Akses (token) di query params atau header X-Order-Token.",
        parameters=[
            OpenApiParameter("token", type=str, location=OpenApiParameter.QUERY, description="Token akses pesanan yang didapat saat checkout"),
        ],
        tags=["Pesanan"]
    ),
)
class OrderViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Mengelola siklus hidup pesanan dari sisi pelanggan.

    Menangani pembuatan pesanan baru (checkout), pengecekan status,
    hingga pengambilan data struk setelah pembayaran berhasil.
    """
    queryset = Order.objects.all()
    permission_classes = [OrderAccessPermission]

    def get_serializer_class(self):
        """
        Menentukan serializer berdasarkan aksi yang dilakukan.
        """
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderReadSerializer
    
    @extend_schema(
        summary="Dapatkan Struk Pesanan",
        description="Menghasilkan data struk digital untuk pesanan yang sudah dibayar.",
        parameters=[
            OpenApiParameter("token", type=str, location=OpenApiParameter.QUERY, description="Token akses pesanan"),
        ],
        responses={200: OpenApiTypes.OBJECT},
        tags=["Pesanan"]
    )
    @action(detail=True, methods=['get'])
    def receipt(self, request, pk=None):
        """
        Menyediakan data struk untuk pesanan yang telah lunas.
        """
        order = self.get_object()

        if order.status == 'pending_payment':
            logger.info(
                "Struk diminta sebelum pembayaran selesai. reference_id=%s",
                order.reference_id,
            )
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

        logger.info(
            "Struk pesanan berhasil disiapkan. reference_id=%s",
            order.reference_id,
        )

        return Response({"status": "success", "data": receipt_data})