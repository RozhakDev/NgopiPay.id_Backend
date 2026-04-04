import random
import string
from datetime import datetime
from django.core import signing
from django.utils.crypto import constant_time_compare

ORDER_ACCESS_SALT = 'ngopipay.order.access'

def generate_reference_id():
    date_str = datetime.now().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"NGOPIPAY-{date_str}-{random_str}"


def generate_order_access_token(order):
    payload = f"{order.pk}:{order.reference_id}"
    return signing.Signer(salt=ORDER_ACCESS_SALT).sign(payload)


def verify_order_access_token(order, token):
    try:
        payload = signing.Signer(salt=ORDER_ACCESS_SALT).unsign(token)
    except signing.BadSignature:
        return False

    expected_payload = f"{order.pk}:{order.reference_id}"
    return constant_time_compare(payload, expected_payload)