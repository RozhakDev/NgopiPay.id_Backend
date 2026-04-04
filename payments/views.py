import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.utils import timezone
from django.db import transaction
from .models import Payment
from .services import PaymenkuService

logger = logging.getLogger(__name__)

class PaymenkuWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        payload = request.data

        verification = PaymenkuService.verify_webhook_payload(payload)
        if not verification.get('verified'):
            reason = verification.get('reason')

            if reason == 'event_not_supported':
                return Response(
                    {"status": "ignored", "message": "Event tidak didukung"},
                    status=status.HTTP_200_OK
                )

            logger.warning(
                "Rejected Paymenku webhook",
                extra={
                    "reason": reason,
                    "reference_id": payload.get('reference_id'),
                    "trx_id": payload.get('trx_id'),
                    "status": payload.get('status'),
                }
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

                    return Response(
                        {"status": "success", "message": "Pembayaran berhasil dicatat"},
                        status=status.HTTP_200_OK
                    )
                elif payment_status in ['expired', 'cancelled']:
                    payment.status = payment_status
                    payment.save()

                    order.status = payment_status
                    order.save()
                    return Response(
                        {"status": "success", "message": f"Pembayaran {payment_status}"},
                        status=status.HTTP_200_OK
                    )
        except Payment.DoesNotExist:
            return Response(
                {"status": "error", "message": "Reference ID tidak ditemukan"},
                  status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({"status": "success"}, status=status.HTTP_200_OK)


class CheckPaymentStatusView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, reference_id, *args, **kwargs):
        result = PaymenkuService.check_status(reference_id)
        return Response(result, status=status.HTTP_200_OK)