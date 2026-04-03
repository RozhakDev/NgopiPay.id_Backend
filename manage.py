#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import sys
import os
from dotenv import load_dotenv


def main():
    """Run administrative tasks."""
    env = os.getenv('ENVIRONMENT', 'development')
    settings_module = 'core.settings.prod' if env == 'production' else 'core.settings.prod'
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Tidak dapat mengimpor Django. Pastikan virtual environment aktif."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()