#!/usr/bin/env python
"""Django's command-line utility for administrative tasks (project-root manage.py).

This script lives at the repository root to allow running
`python manage.py ...` from the project root. It points to the backend
settings module `backend.core.settings` so no path hacks are required.
"""
import os
import sys

# Ensure backend package is importable when running manage.py from project root
ROOT = os.path.dirname(__file__)
BACKEND_PATH = os.path.join(ROOT, 'backend')
if BACKEND_PATH not in sys.path:
    sys.path.insert(0, BACKEND_PATH)


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.core.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
