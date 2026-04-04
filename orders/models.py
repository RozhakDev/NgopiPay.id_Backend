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

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID Pesanan",
        help_text="ID unik yang dibuat otomatis oleh sistem.",
    )
    reference_id = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="ID Referensi",
        help_text="Kode unik untuk integrasi pembayaran dan webhook. Dibuat otomatis oleh sistem.",
    )
    customer_name = models.CharField(
        max_length=100,
        verbose_name="Nama Pelanggan",
        help_text="Nama pelanggan yang akan muncul di dashboard admin dan struk.",
    )
    table_number = models.PositiveIntegerField(
        verbose_name="Nomor Meja",
        help_text="Nomor meja pelanggan sesuai QR Code. Contoh: 5.",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending_payment',
        verbose_name="Status Pesanan",
        help_text="Alur status: menunggu pembayaran, dibayar, diproses, selesai, dibatalkan, atau kedaluwarsa.",
    )
    total_price = models.PositiveIntegerField(
        default=0,
        verbose_name="Total Harga",
        help_text="Total akhir pesanan dalam rupiah. Diisi otomatis berdasarkan item pesanan.",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat Pada")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui Pada")

    class Meta:
        verbose_name = "Pesanan"
        verbose_name_plural = "Data Pesanan"
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.reference_id}] Meja {self.table_number} - {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE,
        verbose_name="Pesanan",
        help_text="Pesanan induk tempat item ini disimpan.",
    )
    menu = models.ForeignKey(
        Menu,
        on_delete=models.PROTECT,
        verbose_name="Menu",
        help_text="Menu yang dipilih pelanggan pada item ini.",
    )

    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Jumlah",
        help_text="Jumlah pesanan untuk menu ini. Minimal 1.",
    )
    price = models.PositiveIntegerField(
        verbose_name="Harga Satuan",
        help_text="Harga menu saat transaksi dibuat. Nilai ini disimpan sebagai snapshot.",
    )
    subtotal = models.PositiveIntegerField(
        verbose_name="Subtotal",
        help_text="Total harga item ini. Dihitung otomatis dari jumlah x harga satuan.",
    )

    class Meta:
        verbose_name = "Item Pesanan"
        verbose_name_plural = "Detail Item Pesanan"

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity}x {self.menu.name} (Pesanan: {self.order.reference_id})"