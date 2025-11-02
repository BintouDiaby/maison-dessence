import os
import sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()

admins = User.objects.filter(is_staff=True).order_by('-id')
if not admins.exists():
    print('No users with is_staff=True found')
else:
    print('Users with is_staff=True (admin candidates):')
    for u in admins:
        print(f'id={u.id} username={u.username!r} email={u.email!r} is_active={u.is_active} is_superuser={u.is_superuser}')

# Also list any superusers specifically
superusers = User.objects.filter(is_superuser=True)
if superusers.exists():
    print('\nSuperusers:')
    for u in superusers:
        print(f'id={u.id} username={u.username!r} email={u.email!r} is_active={u.is_active}')
