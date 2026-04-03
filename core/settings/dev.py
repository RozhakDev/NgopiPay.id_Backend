from .base import *
import os

DEBUG = os.getenv('DEBUG', 'True') == 'True'

env_dev_hosts = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = [host.strip() for host in env_dev_hosts.split(',') if host.strip()]

env_dev_cors = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000')
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in env_dev_cors.split(',') if origin.strip()]

REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'].append('rest_framework.renderers.BrowsableAPIRenderer')