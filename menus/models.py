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

    @property
    def primary_image(self):
        return self.images.order_by('sort_order', 'id').first()

    @property
    def primary_image_url(self):
        primary_image = self.primary_image
        if primary_image and primary_image.image:
            return primary_image.image.url

        return self.image_url


class MenuImage(models.Model):
    menu = models.ForeignKey(Menu, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='menus/%Y/%m/', verbose_name="Gambar Menu")
    alt_text = models.CharField(max_length=120, blank=True, default='', verbose_name="Alt Text")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="Urutan")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Gambar Menu"
        verbose_name_plural = "Gambar Menu"
        ordering = ['sort_order', 'created_at']

    def __str__(self):
        return f"{self.menu.name} - #{self.sort_order}"