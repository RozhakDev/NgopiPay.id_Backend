import requests
import logging
from decimal import Decimal, InvalidOperation
from django.conf import settings

logger = logging.getLogger(__name__)

class PaymenkuService:
    """
    Layanan integrasi dengan Payment Gateway Paymenku.

    Menangani seluruh komunikasi keluar menuju API Paymenku, termasuk
    pembuatan transaksi, pengecekan status, dan validasi webhook.
    """
    BASE_URL = getattr(settings, 'PAYMENKU_BASE_URL', 'https://paymenku.com/api/v1')
    API_KEY = getattr(settings, 'PAYMENKU_API_KEY', '')

    @classmethod
    def get_headers(cls):
        """
        Menyediakan header autentikasi untuk permintaan API.
        """
        return {
            "Authorization": f"Bearer {cls.API_KEY}",
            "Content-Type": "application/json"
        }
    
    @classmethod
    def create_transaction(cls, reference_id, amount, customer_name):
        """
        Mendaftarkan transaksi baru ke sistem Paymenku.

        Fungsi ini akan mengirim data pesanan dan mengharapkan balasan
        berupa ID transaksi (trx_id) dan URL pembayaran (pay_url).

        Args:
            reference_id (str): ID referensi unik pesanan.
            amount (int): Total nominal yang harus dibayar.
            customer_name (str): Nama pelanggan pembayar.

        Returns:
            dict: Hasil transaksi yang memuat status sukses dan data terkait.
        """
        url = f"{cls.BASE_URL}/transaction/create"
        logger.info(
            "Memulai pembuatan transaksi pembayaran. reference_id=%s, amount=%s, customer_name=%s",
            reference_id,
            amount,
            customer_name,
        )

        payload = {
            "reference_id": reference_id,
            "amount": amount,
            "customer_name": customer_name,
            "customer_email": "customer@ngopipay.id",
            "channel_code": "qris",
            "return_url": "https://www.ngopipay.id/payment-done"
        }

        try:
            response = requests.post(url, json=payload, headers=cls.get_headers(), timeout=60)
            response_data = response.json()

            if response.status_code == 200 and response_data.get('status') == 'success':
                logger.info(
                    "Transaksi pembayaran berhasil dibuat. reference_id=%s, trx_id=%s",
                    reference_id,
                    response_data['data']['trx_id'],
                )
                return {
                    "success": True,
                    "trx_id": response_data['data']['trx_id'],
                    "pay_url": response_data['data']['pay_url']
                }
            else:
                logger.error(
                    "Paymenku menolak pembuatan transaksi. reference_id=%s, response=%s",
                    reference_id,
                    response_data,
                )
                return {"success": False, "error": response_data}
        except requests.exceptions.RequestException as e:
            logger.exception(
                "Koneksi ke Paymenku gagal saat membuat transaksi. reference_id=%s",
                reference_id,
            )
            return {"success": False, "error": str(e)}
    
    @classmethod
    def check_status(cls, reference_id):
        """
        Memeriksa status terkini transaksi di sistem Paymenku.

        Digunakan sebagai mekanisme fallback atau sinkronisasi manual
        jika notifikasi otomatis (webhook) tidak diterima.

        Args:
            reference_id (str): ID referensi pesanan yang ingin diperiksa.

        Returns:
            dict: Data status transaksi langsung dari gateway.
        """
        url = f"{cls.BASE_URL}/check-status/{reference_id}"
        try:
            response = requests.get(url, headers=cls.get_headers(), timeout=60)
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.exception(
                "Koneksi ke Paymenku gagal saat pengecekan status. reference_id=%s",
                reference_id,
            )
            return {"status": "error", "message": str(e)}

    @staticmethod
    def format_safe_status_response(reference_id, gateway_result):
        """
        Menyederhanakan data dari gateway untuk dikonsumsi oleh klien.

        Menghilangkan informasi teknis yang tidak perlu dan menyajikan
        data dalam struktur yang konsisten.
        """
        if gateway_result.get('status') != 'success':
            return {
                "status": "error",
                "message": "Gagal mengambil status pembayaran dari gateway.",
            }

        gateway_data = gateway_result.get('data') or {}
        payment_channel = gateway_data.get('payment_channel')
        payment_channel_code = None

        if isinstance(payment_channel, dict):
            payment_channel_code = payment_channel.get('code') or payment_channel.get('name')
        elif isinstance(payment_channel, str):
            payment_channel_code = payment_channel

        return {
            "status": "success",
            "data": {
                "reference_id": gateway_data.get('reference_id') or reference_id,
                "trx_id": gateway_data.get('trx_id'),
                "payment_status": gateway_data.get('status'),
                "payment_channel": payment_channel_code,
                "paid_at": gateway_data.get('paid_at'),
                "created_at": gateway_data.get('created_at'),
                "updated_at": gateway_data.get('updated_at'),
            }
        }

    @staticmethod
    def _to_decimal(value):
        """
        Mengonversi nilai ke tipe Decimal secara aman.
        """
        if value is None:
            return None

        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            return None

    @classmethod
    def verify_webhook_payload(cls, payload):
        """
        Memvalidasi keaslian data yang dikirim melalui webhook.

        Melakukan verifikasi ganda ke API Paymenku untuk memastikan bahwa
        notifikasi pembayaran memang benar dan nominalnya sesuai.

        Args:
            payload (dict): Data webhook yang diterima dari Paymenku.

        Returns:
            dict: Hasil verifikasi yang memuat status keabsahan data.
        """
        event = payload.get('event')
        reference_id = payload.get('reference_id')
        trx_id = payload.get('trx_id')
        incoming_status = payload.get('status')

        if event != 'payment.status_updated':
            return {
                "verified": False,
                "reason": "event_not_supported",
            }

        if not reference_id or not incoming_status:
            return {
                "verified": False,
                "reason": "missing_required_fields",
            }

        gateway_result = cls.check_status(reference_id)
        if gateway_result.get('status') != 'success':
            return {
                "verified": False,
                "reason": "gateway_verification_failed",
                "gateway_result": gateway_result,
            }

        gateway_data = gateway_result.get('data') or {}
        gateway_reference_id = gateway_data.get('reference_id')
        gateway_trx_id = gateway_data.get('trx_id')
        gateway_status = gateway_data.get('status')

        if gateway_reference_id != reference_id:
            return {
                "verified": False,
                "reason": "reference_id_mismatch",
                "gateway_result": gateway_result,
            }

        if gateway_status != incoming_status:
            return {
                "verified": False,
                "reason": "status_mismatch",
                "gateway_result": gateway_result,
            }

        if trx_id and gateway_trx_id and trx_id != gateway_trx_id:
            return {
                "verified": False,
                "reason": "trx_id_mismatch",
                "gateway_result": gateway_result,
            }

        incoming_amount = cls._to_decimal(payload.get('amount'))
        gateway_amount_received = cls._to_decimal(gateway_data.get('amount_received'))
        gateway_amount = cls._to_decimal(gateway_data.get('amount'))

        if incoming_amount is not None:
            if gateway_amount_received is not None and incoming_amount != gateway_amount_received:
                if gateway_amount is None or incoming_amount != gateway_amount:
                    return {
                        "verified": False,
                        "reason": "amount_mismatch",
                        "gateway_result": gateway_result,
                    }

        return {
            "verified": True,
            "gateway_result": gateway_result,
        }