from django.db import models
from orders.models import Order

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Berhasil'),
        ('expired', 'Kedaluwarsa'),
        ('cancelled', 'Dibatalkan'),
    ]

    order = models.OneToOneField(Order, related_name='payment', on_delete=models.CASCADE)
    trx_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="Transaction ID (Paymenku)")
    reference_id = models.CharField(max_length=50, unique=True)
    amount = models.PositiveIntegerField(verbose_name="Nominal Tagihan")
    payment_channel = models.CharField(max_length=50, blank=True, null=True, verbose_name="Metode Pembayaran")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    paid_at = models.DateTimeField(blank=True, null=True, verbose_name="Waktu Terbayar")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pembayaran"
        verbose_name_plural = "Data Pembayaran"
        ordering = ['-created_at']

    def __str__(self):
        return f"Pay: {self.reference_id} - {self.get_status_display()}"