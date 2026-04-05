import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv
from .logging_config import build_logging_config

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def get_required_env(name: str) -> str:
    """
    Mengambil nilai variabel lingkungan yang wajib tersedia.

    Fungsi ini memastikan bahwa konfigurasi penting telah didefinisikan
    dalam environment aplikasi sebelum sistem dijalankan.

    Args:
        name (str): Nama variabel lingkungan yang ingin diambil.

    Returns:
        str: Nilai dari variabel lingkungan tersebut.

    Raises:
        ImproperlyConfigured: Jika variabel lingkungan tidak ditemukan.
    """
    value = os.getenv(name)
    if value:
        return value

    raise ImproperlyConfigured(f"{name} harus disetel di environment.")

SECRET_KEY = get_required_env('SECRET_KEY')

# Paymenku Config
PAYMENKU_API_KEY = get_required_env('PAYMENKU_API_KEY')
PAYMENKU_BASE_URL = os.getenv('PAYMENKU_BASE_URL', 'https://paymenku.com/api/v1')

# Aplikasi Bawaan Django & Aplikasi Pihak Ketiga
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third Party Apps
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    
    # Custom Apps NgopiPay.id
    'menus',
    'orders',
    'payments',
    'reports',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'core.middleware.RequestContextMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'id' # Bahasa Indonesia
TIME_ZONE = 'Asia/Jakarta' # WIB
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Konfigurasi REST Framework
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Konfigurasi Dokumentasi Swagger
SPECTACULAR_SETTINGS = {
    'TITLE': 'NgopiPay.id API',
    'DESCRIPTION': (
        'Dokumentasi resmi API NgopiPay.id. '
        'Sistem pemesanan makanan/minuman berbasis QR Code yang terintegrasi dengan Payment Gateway Paymenku. '
        'Memungkinkan pelanggan memesan dari meja tanpa login dan admin memproses pesanan melalui dashboard.'
    ),
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'CONTACT': {
        'name': 'Tim Pengembang NgopiPay.id',
        'url': 'https://www.ngopipay.my.id',
        'email': 'support@ngopipay.my.id',
    },
    'TAGS': [
        {'name': 'Menu', 'description': 'Manajemen katalog makanan dan minuman'},
        {'name': 'Pesanan', 'description': 'Proses pemesanan, checkout, dan status pesanan pelanggan'},
        {'name': 'Pembayaran', 'description': 'Integrasi payment gateway dan pengecekan status transaksi'},
        {'name': 'Admin - Pesanan', 'description': 'Manajemen operasional pesanan untuk kasir/dapur'},
        {'name': 'Admin - Laporan', 'description': 'Laporan penjualan dan statistik bisnis'},
    ],
}

LOGGING = build_logging_config(BASE_DIR)