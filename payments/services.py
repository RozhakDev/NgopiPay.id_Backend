import requests
import logging
from decimal import Decimal, InvalidOperation
from django.conf import settings

logger = logging.getLogger(__name__)

class PaymenkuService:
    BASE_URL = getattr(settings, 'PAYMENKU_BASE_URL', 'https://paymenku.com/api/v1')
    API_KEY = getattr(settings, 'PAYMENKU_API_KEY', '')

    @classmethod
    def get_headers(cls):
        return {
            "Authorization": f"Bearer {cls.API_KEY}",
            "Content-Type": "application/json"
        }
    
    @classmethod
    def create_transaction(cls, reference_id, amount, customer_name):
        url = f"{cls.BASE_URL}/transaction/create"

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
                return {
                    "success": True,
                    "trx_id": response_data['data']['trx_id'],
                    "pay_url": response_data['data']['pay_url']
                }
            else:
                logger.error(f"Paymenku Error: {response_data}")
                return {"success": False, "error": response_data}
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP Request failed: {e}")
            return {"success": False, "error": str(e)}
    
    @classmethod
    def check_status(cls, reference_id):
        url = f"{cls.BASE_URL}/check-status/{reference_id}"
        try:
            response = requests.get(url, headers=cls.get_headers(), timeout=60)
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def _to_decimal(value):
        if value is None:
            return None

        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            return None

    @classmethod
    def verify_webhook_payload(cls, payload):
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