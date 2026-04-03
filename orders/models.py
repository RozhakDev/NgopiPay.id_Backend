import uuid
from django.db import models
from menus.models import Menu

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending_payment', 'Menunggu Pembayaran'),
        ('paid', 'Sudah Dibayar'),
        ('cooking', 'Sedang Diproses'),
        ('done', 'Selesai'),
        ('cancelled', 'Dibatalkan'),
        ('expired', 'Kedaluwarsa'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference_id = models.CharField(max_length=50, unique=True, verbose_name="ID Referensi")
    customer_name = models.CharField(max_length=100, verbose_name="Nama Pelanggan")
    table_number = models.PositiveIntegerField(verbose_name="Nomor Meja")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_payment')
    total_price = models.PositiveIntegerField(default=0, verbose_name="Total Harga")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pesanan"
        verbose_name_plural = "Data Pesanan"
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.reference_id}] Meja {self.table_number} - {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.PROTECT)

    quantity = models.PositiveIntegerField(default=1, verbose_name="Jumlah")
    price = models.PositiveIntegerField(verbose_name="Harga Satuan (Snapshot)")
    subtotal = models.PositiveIntegerField(verbose_name="Subtotal")

    class Meta:
        verbose_name = "Item Pesanan"
        verbose_name_plural = "Detail Item Pesanan"

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity}x {self.menu.name} (Pesanan: {self.order.reference_id})"