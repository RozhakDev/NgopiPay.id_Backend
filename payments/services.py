import requests
import logging
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