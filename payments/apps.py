from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    """
    Konfigurasi utama untuk modul sistem pembayaran.

    Berfungsi sebagai jembatan integrasi dengan layanan payment gateway,
    memproses transaksi digital, dan memvalidasi notifikasi pembayaran.
    """
    name = 'payments'