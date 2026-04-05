from django.apps import AppConfig


class ReportsConfig(AppConfig):
    """
    Konfigurasi utama untuk modul pelaporan dan statistik.

    Menyediakan fitur agregasi data penjualan untuk membantu pihak admin
    dalam memantau performa bisnis secara harian hingga bulanan.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reports'