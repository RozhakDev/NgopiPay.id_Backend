from django.apps import AppConfig


class OrdersConfig(AppConfig):
    """
    Konfigurasi utama untuk modul manajemen pesanan.

    Menangani seluruh siklus hidup pesanan pelanggan, mulai dari proses
    pembuatan keranjang, checkout, hingga pelacakan status pesanan.
    """
    name = 'orders'