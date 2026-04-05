import string
from datetime import datetime
from django.core import signing
from django.utils.crypto import constant_time_compare
from django.utils.crypto import get_random_string

ORDER_ACCESS_SALT = 'ngopipay.order.access'

def generate_reference_id():
    """
    Menghasilkan ID referensi unik untuk setiap pesanan.

    Menggabungkan format tanggal saat ini dengan string acak untuk 
    memastikan keunikan identitas pesanan di sistem.

    Returns:
        str: Kode referensi pesanan (misal: NGOPIPAY-20260405-ABCD1234EF).
    """
    date_str = datetime.now().strftime('%Y%m%d')
    random_str = get_random_string(10, allowed_chars=string.ascii_uppercase + string.digits)
    return f"NGOPIPAY-{date_str}-{random_str}"


def generate_order_access_token(order):
    """
    Membuat token akses digital untuk satu pesanan tertentu.

    Token ini digunakan pelanggan untuk mengakses status pesanan mereka
    tanpa harus melewati proses login konvensional.

    Args:
        order (Order): Objek pesanan yang akan dibuatkan tokennya.

    Returns:
        str: String token akses yang telah ditandatangani secara aman.
    """
    payload = f"{order.pk}:{order.reference_id}"
    return signing.Signer(salt=ORDER_ACCESS_SALT).sign(payload)


def verify_order_access_token(order, token):
    """
    Memvalidasi apakah token akses yang dikirim klien sah.

    Memastikan token belum dimanipulasi dan memang ditujukan untuk
    mengakses data pesanan yang diminta.

    Args:
        order (Order): Objek pesanan yang ingin diakses.
        token (str): Token akses yang dikirim oleh klien.

    Returns:
        bool: Mengembalikan True jika token valid dan sesuai.
    """
    try:
        payload = signing.Signer(salt=ORDER_ACCESS_SALT).unsign(token)
    except signing.BadSignature:
        return False

    expected_payload = f"{order.pk}:{order.reference_id}"
    return constant_time_compare(payload, expected_payload)