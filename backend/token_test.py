import os
import sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
from django.test import Client
import json

User = get_user_model()
username = 'apitest'
email = 'apitest@example.test'
password = 'Testpass123'

u, created = User.objects.get_or_create(username=username, defaults={'email': email})
if created:
    u.set_password(password)
    u.is_active = True
    u.save()
    print('Created user', username)
else:
    u.set_password(password)
    u.is_active = True
    u.save()
    print('Updated user', username)

c = Client()
resp = c.post('/api/auth/token/', json.dumps({'email': email, 'password': password}), content_type='application/json')
print('STATUS', resp.status_code)
print('CONTENT', resp.content)

# Also try username login
resp2 = c.post('/api/auth/token/', json.dumps({'username': username, 'password': password}), content_type='application/json')
print('STATUS2', resp2.status_code)
print('CONTENT2', resp2.content)
