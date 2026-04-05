from django.db import models

class Menu(models.Model):
    """
    Representasi data katalog makanan dan minuman.

    Menyimpan informasi inti mengenai produk seperti nama, harga, deskripsi,
    hingga status ketersediaan menu untuk dipesan oleh pelanggan.
    """
    name = models.CharField(
        max_length=100,
        verbose_name="Nama Menu",
        help_text="Nama yang ditampilkan ke pelanggan. Contoh: Es Kopi Susu.",
    )
    price = models.PositiveIntegerField(
        verbose_name="Harga",
        help_text="Harga per porsi dalam rupiah, tanpa tanda titik atau koma. Contoh: 15000.",
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Deskripsi",
        help_text="Keterangan singkat menu. Contoh: Kopi susu dengan gula aren.",
    )
    image_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="URL Gambar",
        help_text="Isi jika gambar menu tersedia dalam bentuk tautan. Contoh: https://domain.com/gambar.jpg.",
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name="Tersedia",
        help_text="Aktifkan jika menu bisa dipesan. Nonaktifkan jika menu sedang habis atau tidak dijual.",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat Pada")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui Pada")

    class Meta:
        """
        Konfigurasi tambahan untuk model Menu.
        """
        verbose_name = "Menu"
        verbose_name_plural = "Data Menu"
        ordering = ['-is_available', 'name']

    def __str__(self):
        """
        Memberikan representasi nama menu dan harganya.
        """
        return f"{self.name} - Rp{self.price}"

    @property
    def primary_image(self):
        """
        Mengambil objek gambar utama dari galeri menu.

        Returns:
            MenuImage: Objek gambar pertama berdasarkan urutan sort_order.
        """
        return self.images.order_by('sort_order', 'id').first()

    @property
    def primary_image_url(self):
        """
        Menentukan URL gambar terbaik untuk ditampilkan.

        Memprioritaskan gambar dari galeri internal, jika tidak ada maka
        akan menggunakan URL gambar eksternal (fallback).

        Returns:
            str: URL gambar yang dapat diakses.
        """
        primary_image = self.primary_image
        if primary_image and primary_image.image:
            return primary_image.image.url

        return self.image_url


class MenuImage(models.Model):
    """
    Menyimpan galeri gambar pendukung untuk setiap menu.

    Memungkinkan satu menu memiliki banyak gambar dengan urutan tampilan
    yang dapat diatur secara manual.
    """
    menu = models.ForeignKey(
        Menu,
        related_name='images',
        on_delete=models.CASCADE,
        verbose_name="Menu",
        help_text="Pilih menu yang akan diberi gambar tambahan.",
    )
    image = models.ImageField(
        upload_to='menus/%Y/%m/',
        verbose_name="Gambar Menu",
        help_text="Unggah gambar yang jelas agar pelanggan mudah mengenali menu.",
    )
    alt_text = models.CharField(
        max_length=120,
        blank=True,
        default='',
        verbose_name="Teks Alternatif",
        help_text="Teks singkat untuk menjelaskan gambar. Berguna jika gambar gagal dimuat.",
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name="Urutan",
        help_text="Semakin kecil angka, semakin dulu gambar ditampilkan.",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat Pada")

    class Meta:
        """
        Konfigurasi tambahan untuk model Gambar Menu.
        """
        verbose_name = "Gambar Menu"
        verbose_name_plural = "Gambar Menu"
        ordering = ['sort_order', 'created_at']

    def __str__(self):
        """
        Memberikan representasi menu dan urutan gambarnya.
        """
        return f"{self.menu.name} - #{self.sort_order}"