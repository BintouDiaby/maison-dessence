import os
import sys
from datetime import datetime
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()

qs = User.objects.all().order_by('-id')[:10]
print('ID  | username | email | is_active | date_joined')
for u in qs:
    dj = u.date_joined.isoformat() if getattr(u, 'date_joined', None) else 'N/A'
    print(f"{u.id} | {u.username!s} | {u.email!s} | {u.is_active} | {dj}")
