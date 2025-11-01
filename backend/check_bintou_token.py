import os
import sys
import json
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()
from django.test import Client

c = Client()
resp = c.post('/api/auth/token/', json.dumps({'username':'bintou','password':'bintou1234'}), content_type='application/json')
print('STATUS', resp.status_code)
print(resp.content.decode())
