import logging
from django.contrib import admin
from .models import Payment

logger = logging.getLogger(__name__)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Mengatur tampilan dan pengelolaan data pembayaran di panel admin.

    Memudahkan pihak admin untuk memantau status transaksi, mencari referensi
    pembayaran, serta melihat detail waktu pembayaran berhasil.
    """
    list_display = ('reference_id', 'order', 'amount', 'payment_channel', 'status', 'paid_at')
    list_filter = ('status', 'payment_channel')
    search_fields = ('reference_id', 'trx_id', 'order__customer_name')
    readonly_fields = ('reference_id', 'order', 'trx_id', 'amount', 'created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        """
        Mencatat aktivitas penyimpanan data pembayaran melalui admin.
        """
        super().save_model(request, obj, form, change)
        logger.info(
            "Pembayaran disimpan melalui Django Admin. user=%s, reference_id=%s, status=%s",
            request.user,
            obj.reference_id,
            obj.status,
        )

    def delete_model(self, request, obj):
        """
        Mencatat aktivitas penghapusan data pembayaran melalui admin.
        """
        logger.info(
            "Pembayaran dihapus melalui Django Admin. user=%s, reference_id=%s",
            request.user,
            obj.reference_id,
        )
        super().delete_model(request, obj)