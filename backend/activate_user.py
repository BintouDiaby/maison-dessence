import os
import sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Ensure backend package is on path so Django project modules are importable
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()

u = User.objects.filter(is_active=False).order_by('-id').first()
print('FOUND:', getattr(u, 'username', None), getattr(u, 'email', None))
if u:
    u.is_active = True
    u.save()
    print('ACTIVATED')
else:
    print('NO_INACTIVE_USER')
