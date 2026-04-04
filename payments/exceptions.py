from rest_framework.exceptions import APIException


class PaymentGatewayError(APIException):
    status_code = 502
    default_detail = 'Gagal membuat transaksi pembayaran.'
    default_code = 'payment_gateway_error'