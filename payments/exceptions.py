from rest_framework.exceptions import APIException


class PaymentGatewayError(APIException):
    """
    Menangani kegagalan komunikasi dengan payment gateway.

    Eksepsi ini dilemparkan ketika sistem gagal membuat transaksi atau
    mendapatkan respon yang valid dari server Paymenku.
    """
    status_code = 502
    default_detail = 'Gagal membuat transaksi pembayaran.'
    default_code = 'payment_gateway_error'