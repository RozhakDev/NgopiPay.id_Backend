from contextvars import ContextVar
from uuid import uuid4
import logging

request_id_var = ContextVar("request_id", default="-")
request_method_var = ContextVar("request_method", default="-")
request_path_var = ContextVar("request_path", default="-")
request_user_var = ContextVar("request_user", default="-")

def generate_request_id() -> str:
    """
    Menghasilkan identitas unik untuk pelacakan permintaan.

    Menggunakan format UUID hex untuk memastikan setiap permintaan HTTP
    memiliki ID yang berbeda dan mudah dilacak di dalam log.

    Returns:
        str: String identitas unik berformat hexadecimal.
    """
    return uuid4().hex

def set_request_context(*, request_id: str, method: str = "-", path: str = "-", user: str = "-") -> None:
    """
    Mengatur informasi konteks untuk permintaan saat ini.

    Menyimpan detail teknis permintaan ke dalam variabel konteks agar dapat
    diakses secara otomatis oleh sistem logging di seluruh alur eksekusi.

    Args:
        request_id (str): Identitas unik permintaan.
        method (str): Metode HTTP yang digunakan.
        path (str): Jalur URL yang diakses.
        user (str): Identitas pengguna yang melakukan permintaan.
    """
    request_id_var.set(request_id)
    request_method_var.set(method)
    request_path_var.set(path)
    request_user_var.set(user)

def clear_request_context() -> None:
    """
    Membersihkan seluruh informasi konteks yang tersimpan.

    Mengembalikan seluruh nilai variabel konteks ke nilai default setelah
    permintaan selesai diproses untuk mencegah kebocoran data antar permintaan.
    """
    request_id_var.set("-")
    request_method_var.set("-")
    request_path_var.set("-")
    request_user_var.set("-")

class RequestContextFilter(logging.Filter):
    """
    Filter logging untuk menyisipkan informasi konteks ke dalam record log.

    Memungkinkan setiap baris log yang dihasilkan sistem secara otomatis
    memuat ID permintaan, metode, jalur, dan identitas pengguna.
    """
    def filter(self, record):
        """
        Menambahkan atribut konteks ke dalam record log sebelum dicatat.
        """
        record.request_id = request_id_var.get()
        record.request_method = request_method_var.get()
        record.request_path = request_path_var.get()
        record.request_user = request_user_var.get()
        return True