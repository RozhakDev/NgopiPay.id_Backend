import logging
from django.contrib import admin
from .models import Order, OrderItem

logger = logging.getLogger(__name__)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price', 'subtotal')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('reference_id', 'customer_name', 'table_number', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('reference_id', 'customer_name', 'table_number')
    readonly_fields = ('id', 'reference_id', 'total_price', 'created_at', 'updated_at')
    inlines = [OrderItemInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        logger.info(
            "Pesanan disimpan melalui Django Admin. user=%s, reference_id=%s, status=%s",
            request.user,
            obj.reference_id,
            obj.status,
        )

    def delete_model(self, request, obj):
        logger.info(
            "Pesanan dihapus melalui Django Admin. user=%s, reference_id=%s",
            request.user,
            obj.reference_id,
        )
        super().delete_model(request, obj)