# NgopiPay.id - Backend

**NgopiPay.id** merupakan sistem pemesanan makanan berbasis web yang dirancang untuk membantu UMKM kuliner dalam mendigitalisasi proses pemesanan. Sistem ini memungkinkan pelanggan melakukan pemesanan langsung dari meja melalui QR code tanpa memerlukan proses login.

Backend pada sistem ini berperan sebagai pusat logika bisnis, pengelolaan data pesanan, serta integrasi dengan payment gateway. Seluruh alur transaksi, validasi pembayaran, dan pengelolaan status pesanan dikendalikan melalui service backend.

## Gambaran Sistem

Sistem ini dibangun untuk menggantikan proses pemesanan manual yang umumnya terjadi di kasir menjadi alur digital yang lebih efisien. Pelanggan cukup melakukan scan QR code, memilih menu, melakukan pembayaran, dan pesanan akan langsung diproses oleh admin atau dapur setelah pembayaran terverifikasi.

Pendekatan ini bertujuan untuk mengurangi antrean, meminimalisir kesalahan pencatatan, serta memastikan setiap pesanan tervalidasi sebelum diproses.

## Peran Backend

Backend bertanggung jawab terhadap beberapa fungsi utama dalam sistem:

- Mengelola pembuatan dan penyimpanan data pesanan
- Mengatur lifecycle status pesanan
- Mengintegrasikan sistem dengan payment gateway
- Memproses webhook sebagai sumber validasi pembayaran
- Menyediakan API untuk kebutuhan frontend customer dan admin
- Menyediakan data pesanan untuk dashboard admin melalui mekanisme polling

Backend menjadi komponen utama yang memastikan konsistensi data dan kontrol penuh terhadap alur bisnis sistem.

## Alur Bisnis Utama

Alur sistem dimulai ketika pelanggan mengakses menu melalui QR code yang terhubung dengan nomor meja. Pelanggan kemudian memilih menu dan melakukan checkout, sehingga sistem akan membuat pesanan dengan status awal *pending_payment*.

Setelah itu, backend akan membuat transaksi ke payment gateway dan mengembalikan URL pembayaran. Ketika pembayaran berhasil dilakukan, sistem menerima notifikasi melalui webhook dan memperbarui status pesanan menjadi *paid*.

Pesanan yang telah berstatus *paid* akan tersedia pada dashboard admin untuk diproses lebih lanjut hingga selesai. Pendekatan ini memastikan bahwa hanya pesanan yang sudah dibayar yang dapat diproses oleh sistem.

## Teknologi

Backend sistem ini dibangun menggunakan stack berikut:

- Django sebagai framework utama
- Django REST Framework untuk penyediaan API
- SQLite sebagai database pada tahap awal
- Integrasi payment gateway menggunakan Paymenku
- Mekanisme polling untuk pembaruan data admin (tanpa WebSocket)

Pemilihan teknologi difokuskan pada kesederhanaan, kemudahan deployment, serta kompatibilitas dengan shared hosting.

## Karakteristik Sistem

Beberapa karakteristik utama dari backend NgopiPay.id:

- Tidak menggunakan autentikasi untuk customer
- Menggunakan webhook sebagai sumber utama validasi pembayaran
- Dirancang untuk beban ringan hingga menengah (skala UMKM)
- Mengutamakan konsistensi data dan kesederhanaan arsitektur

## Dokumentasi

Dokumentasi sistem tersedia dalam dua bentuk:

- Dokumentasi API (Swagger)
- Dokumen spesifikasi sistem (SRS)  

Dokumen SRS berisi penjelasan lengkap mengenai kebutuhan sistem, alur bisnis, serta desain teknis yang digunakan sebagai acuan pengembangan.

## Kredit

Ide sistem ini berasal dari: Zahra Tsuroyya Poetri

Implementasi backend dilakukan oleh: Rozhak

## Catatan

Proyek ini dikembangkan dalam konteks akademik dan eksplorasi implementasi sistem berbasis web untuk UMKM. Fokus utama berada pada kesesuaian solusi dengan kebutuhan nyata di lapangan serta efisiensi implementasi pada infrastruktur terbatas.