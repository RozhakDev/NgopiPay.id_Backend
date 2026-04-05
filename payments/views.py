import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.utils import timezone
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import Payment
from .services import PaymenkuService
from orders.utils import verify_order_access_token

logger = logging.getLogger(__name__)

class PaymenkuWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Webhook Notifikasi Pembayaran (Paymenku)",
        description="Endpoint publik untuk menerima notifikasi otomatis dari Paymenku saat status transaksi berubah.",
        request=OpenApiTypes.OBJECT,
        responses={200: OpenApiTypes.OBJECT},
        tags=["Pembayaran"]
    )
    def post(self, request, *args, **kwargs):
        payload = request.data
        logger.info(
            "Webhook Paymenku diterima. reference_id=%s, status=%s, event=%s",
            payload.get('reference_id'),
            payload.get('status'),
            payload.get('event'),
        )

        verification = PaymenkuService.verify_webhook_payload(payload)
        if not verification.get('verified'):
            reason = verification.get('reason')

            if reason == 'event_not_supported':
                logger.info(
                    "Webhook diabaikan karena event tidak didukung. reference_id=%s",
                    payload.get('reference_id'),
                )
                return Response(
                    {"status": "ignored", "message": "Event tidak didukung"},
                    status=status.HTTP_200_OK
                )

            log_message = (
                "Webhook Paymenku ditolak. alasan=%s, reference_id=%s, trx_id=%s, status=%s"
            )
            if reason == 'gateway_verification_failed':
                logger.error(
                    log_message,
                    reason,
                    payload.get('reference_id'),
                    payload.get('trx_id'),
                    payload.get('status'),
                )
            else:
                logger.warning(
                    log_message,
                    reason,
                    payload.get('reference_id'),
                    payload.get('trx_id'),
                    payload.get('status'),
                )

            if reason == 'gateway_verification_failed':
                return Response(
                    {"status": "error", "message": "Validasi webhook ke payment gateway gagal"},
                    status=status.HTTP_502_BAD_GATEWAY
                )

            return Response(
                {"status": "error", "message": "Payload webhook tidak valid"},
                status=status.HTTP_400_BAD_REQUEST
            )

        reference_id = payload.get('reference_id')
        payment_status = payload.get('status')

        try:
            payment = Payment.objects.get(reference_id=reference_id)
            order = payment.order

            with transaction.atomic():
                if payment_status == 'paid' and payment.status != 'paid':
                    payment.status = 'paid'
                    payment.paid_at = timezone.now()
                    payment.save()

                    order.status = 'paid'
                    order.save()
                    logger.info(
                        "Pembayaran berhasil dicatat. reference_id=%s, order_id=%s",
                        reference_id,
                        order.pk,
                    )

                    return Response(
                        {"status": "success", "message": "Pembayaran berhasil dicatat"},
                        status=status.HTTP_200_OK
                    )
                elif payment_status in ['expired', 'cancelled']:
                    payment.status = payment_status
                    payment.save()

                    order.status = payment_status
                    order.save()
                    logger.info(
                        "Status pembayaran diperbarui. reference_id=%s, status=%s, order_id=%s",
                        reference_id,
                        payment_status,
                        order.pk,
                    )
                    return Response(
                        {"status": "success", "message": f"Pembayaran {payment_status}"},
                        status=status.HTTP_200_OK
                    )
        except Payment.DoesNotExist:
            logger.warning(
                "Reference ID pembayaran tidak ditemukan. reference_id=%s",
                reference_id,
            )
            return Response(
                {"status": "error", "message": "Reference ID tidak ditemukan"},
                  status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({"status": "success"}, status=status.HTTP_200_OK)


class CheckPaymentStatusView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Cek Status Pembayaran (Manual Check)",
        description="Melakukan sinkronisasi status pembayaran langsung ke API Paymenku sebagai fallback jika webhook terlambat.",
        parameters=[
            OpenApiParameter("reference_id", type=str, location=OpenApiParameter.PATH, description="Reference ID internal"),
            OpenApiParameter("token", type=str, location=OpenApiParameter.QUERY, description="Token akses pesanan"),
        ],
        responses={200: OpenApiTypes.OBJECT},
        tags=["Pembayaran"]
    )
    def get(self, request, reference_id, *args, **kwargs):
        token = request.query_params.get('token') or request.headers.get('X-Order-Token')
        logger.info(
            "Pengecekan status pembayaran dimulai. reference_id=%s",
            reference_id,
        )

        try:
            payment = Payment.objects.select_related('order').get(reference_id=reference_id)
        except Payment.DoesNotExist:
            logger.warning(
                "Pengecekan status pembayaran gagal. reference_id tidak ditemukan=%s",
                reference_id,
            )
            return Response(
                {"status": "error", "message": "Reference ID tidak ditemukan"},
                status=status.HTTP_404_NOT_FOUND
            )

        if not token or not verify_order_access_token(payment.order, token):
            logger.warning(
                "Token akses order tidak valid. reference_id=%s",
                reference_id,
            )
            return Response(
                {"status": "error", "message": "Token akses order tidak valid."},
                status=status.HTTP_403_FORBIDDEN
            )

        result = PaymenkuService.check_status(reference_id)
        safe_result = PaymenkuService.format_safe_status_response(reference_id, result)
        http_status = status.HTTP_200_OK if safe_result.get('status') == 'success' else status.HTTP_502_BAD_GATEWAY
        logger.info(
            "Pengecekan status pembayaran selesai. reference_id=%s, hasil=%s",
            reference_id,
            safe_result.get('status'),
        )
        return Response(safe_result, status=http_status)