from django.db import models
from orders.models import Order

class Payment(models.Model):
    """
    Menyimpan informasi lengkap mengenai transaksi pembayaran.

    Model ini mencatat status pembayaran, nominal tagihan, hingga tautan
    pembayaran yang dihasilkan oleh gateway Paymenku.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Berhasil'),
        ('expired', 'Kedaluwarsa'),
        ('cancelled', 'Dibatalkan'),
    ]

    order = models.OneToOneField(
        Order,
        related_name='payment',
        on_delete=models.CASCADE,
        verbose_name="Pesanan",
        help_text="Satu pembayaran hanya untuk satu pesanan.",
    )
    trx_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="ID Transaksi Paymenku",
        help_text="ID transaksi dari payment gateway setelah pembayaran dibuat.",
    )
    reference_id = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="ID Referensi",
        help_text="Harus sama dengan referensi pesanan yang dibayar.",
    )
    amount = models.PositiveIntegerField(
        verbose_name="Nominal Tagihan",
        help_text="Nominal yang harus dibayar oleh pelanggan dalam rupiah.",
    )
    payment_channel = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Metode Pembayaran",
        help_text="Metode yang dipakai untuk membayar. Contoh: qris.",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Status Pembayaran",
        help_text="Menunjukkan kondisi pembayaran saat ini: pending, paid, expired, atau cancelled.",
    )

    pay_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="URL Pembayaran",
        help_text="Tautan pembayaran yang dibuka pelanggan untuk menyelesaikan transaksi.",
    )

    paid_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Waktu Terbayar",
        help_text="Waktu saat pembayaran berhasil dicatat oleh sistem.",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat Pada")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui Pada")

    class Meta:
        """
        Konfigurasi tambahan untuk model Pembayaran.
        """
        verbose_name = "Pembayaran"
        verbose_name_plural = "Data Pembayaran"
        ordering = ['-created_at']

    def __str__(self):
        """
        Memberikan representasi kode referensi dan status pembayaran.
        """
        return f"Pay: {self.reference_id} - {self.get_status_display()}"