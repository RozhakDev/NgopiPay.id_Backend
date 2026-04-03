from django.contrib import admin
from .models import Order, OrderItem

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