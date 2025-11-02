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

username_to_delete = 'Bintou'  # duplicate with 'bintou'
try:
    u = User.objects.get(username=username_to_delete)
    print('Found user:', u.id, u.username, u.email, 'is_staff=', u.is_staff)
    # avoid deleting a superuser unintentionally
    if u.is_superuser or u.is_staff:
        print('Refusing to delete a staff/superuser account via this script.')
    else:
        u.delete()
        print('Deleted user', username_to_delete)
except User.DoesNotExist:
    print('User not found:', username_to_delete)
except Exception as e:
    print('Error:', e)
