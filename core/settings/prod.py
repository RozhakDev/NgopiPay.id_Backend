from .base import *
import os

DEBUG = False

ALLOWED_HOSTS = ['nongki.my.id', 'www.nongki.my.id', 'api.nongki.my.id']

CORS_ALLOWED_ORIGINS = [
    "https://nongki.my.id",
    "https://www.nongki.my.id",
]

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

STATIC_ROOT = os.path.join(BASE_DIR, 'public_html', 'static')