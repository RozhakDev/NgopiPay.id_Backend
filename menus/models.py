from django.db import models

class Menu(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nama Menu")
    price = models.PositiveIntegerField(verbose_name="Harga")
    description = models.TextField(blank=True, null=True, verbose_name="Deskripsi")
    image_url = models.URLField(blank=True, null=True, verbose_name="URL Gambar")
    is_available = models.BooleanField(default=True, verbose_name="Tersedia?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Menu"
        verbose_name_plural = "Data Menu"
        ordering = ['-is_available', 'name']

    def __str__(self):
        return f"{self.name} - Rp{self.price}"