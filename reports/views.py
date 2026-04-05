import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from orders.models import Order

logger = logging.getLogger(__name__)

class SalesReportView(APIView):
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(
        summary="Laporan Penjualan (Admin)",
        description="Melihat ringkasan total pendapatan dan jumlah pesanan dalam periode tertentu.",
        parameters=[
            OpenApiParameter("period", type=str, description="Periode laporan: daily, weekly, monthly. Default: daily."),
        ],
        responses={200: OpenApiTypes.OBJECT},
        tags=["Admin - Laporan"]
    )
    def get(self, request, *args, **kwargs):
        period = request.query_params.get('period', 'daily')
        now = timezone.now()

        if period == 'weekly':
            start_date = now - timedelta(days=7)
        elif period == 'monthly':
            start_date = now - timedelta(days=30)
        else:
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)

        valid_orders = Order.objects.filter(
            created_at__gte=start_date,
            status__in=['paid', 'cooking', 'done']
        )

        aggregation = valid_orders.aggregate(
            total_revenue=Sum('total_price'),
            total_orders=Count('id')
        )

        logger.info(
            "Laporan penjualan berhasil dibuat. period=%s, total_orders=%s, total_revenue=%s",
            period,
            aggregation['total_orders'] or 0,
            aggregation['total_revenue'] or 0,
        )

        return Response({
            "status": "success",
            "data": {
                "period": period,
                "start_date": start_date.isoformat(),
                "end_date": now.isoformat(),
                "total_orders": aggregation['total_orders'] or 0,
                "total_revenue": aggregation['total_revenue'] or 0
            }
        })