from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.utils import timezone
from .models import Payment
from orders.models import Order
from .services import PaymenkuService

class PaymenkuWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        payload = request.data

        event = payload.get('event')
        reference_id = payload.get('reference_id')
        payment_status = payload.get('status')

        if event != 'payment.status_updated':
            return Response(
                {"status": "ignored", "message": "Event tidak didukung"},
                  status=status.HTTP_200_OK
            )
        
        try:
            payment = Payment.objects.get(reference_id=reference_id)
            order = payment.order

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