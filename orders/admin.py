import logging
from django.contrib import admin
from .models import Order, OrderItem

logger = logging.getLogger(__name__)

class OrderItemInline(admin.TabularInline):
    """
    Menyediakan antarmuka pengeditan item pesanan secara inline.

    Memungkinkan admin untuk melihat dan mengelola daftar menu yang dipesan
    langsung dari halaman detail pesanan utama.
    """
    model = OrderItem
    extra = 0
    readonly_fields = ('price', 'subtotal')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Pusat pengelolaan data pesanan di panel admin Django.

    Menyediakan fitur pemantauan status pesanan, pencarian pelanggan,
    hingga integrasi tampilan item pesanan secara terpadu.
    """
    list_display = ('reference_id', 'customer_name', 'table_number', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('reference_id', 'customer_name', 'table_number')
    readonly_fields = ('id', 'reference_id', 'total_price', 'created_at', 'updated_at')
    inlines = [OrderItemInline]

    def save_model(self, request, obj, form, change):
        """
        Mencatat aktivitas penyimpanan data pesanan melalui admin.
        """
        super().save_model(request, obj, form, change)
        logger.info(
            "Pesanan disimpan melalui Django Admin. user=%s, reference_id=%s, status=%s",
            request.user,
            obj.reference_id,
            obj.status,
        )

    def delete_model(self, request, obj):
        """
        Mencatat aktivitas penghapusan data pesanan melalui admin.
        """
        logger.info(
            "Pesanan dihapus melalui Django Admin. user=%s, reference_id=%s",
            request.user,
            obj.reference_id,
        )
        super().delete_model(request, obj)