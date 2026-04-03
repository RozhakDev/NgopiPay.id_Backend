from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('reference_id', 'order', 'amount', 'payment_channel', 'status', 'paid_at')
    list_filter = ('status', 'payment_channel')
    search_fields = ('reference_id', 'trx_id', 'order__customer_name')
    readonly_fields = ('reference_id', 'order', 'trx_id', 'amount', 'created_at', 'updated_at')