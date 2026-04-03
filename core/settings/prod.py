from .base import *
import os

DEBUG = os.getenv('DEBUG', 'False') == 'True'

env_prod_hosts = os.getenv('ALLOWED_HOSTS', 'yourdomain.com,www.yourdomain.com')
ALLOWED_HOSTS = [host.strip() for host in env_prod_hosts.split(',') if host.strip()]

env_prod_cors = os.getenv('CORS_ALLOWED_ORIGINS', 'https://yourdomain.com,https://www.yourdomain.com')
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in env_prod_cors.split(',') if origin.strip()]

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

STATIC_ROOT = os.path.join(BASE_DIR, 'public_html', 'static')