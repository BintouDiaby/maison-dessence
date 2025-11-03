import os
import sys
import json

# Run from backend/ as working dir
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.conf import settings

HAS_MODEL = True
try:
    from products.models import Product
except Exception as e:
    HAS_MODEL = False
    Product = None

print('DJANGO_SETTINGS_MODULE=', os.environ.get('DJANGO_SETTINGS_MODULE'))
print('Working dir:', os.getcwd())
print('HAS_MODEL:', HAS_MODEL)
if HAS_MODEL and Product is not None:
    try:
        qs = Product.objects.all()
        print('Products in DB:', qs.count())
        print('Sample (first 10):')
        for p in qs.order_by('id')[:10]:
            print('-', p.id, getattr(p, 'name', None))
    except Exception as e:
        print('Error querying Product:', repr(e))

# Check fallback JSON
data_file = os.path.join(os.path.dirname(__file__), 'products', 'data', 'products.json')
print('Fallback JSON path:', data_file)
if os.path.exists(data_file):
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print('Fallback JSON entries:', len(data) if isinstance(data, list) else 'not a list')
    except Exception as e:
        print('Error reading fallback JSON:', repr(e))
else:
    print('Fallback JSON not found')

# Print migrations status hint (we won't call management here to avoid side effects)
print('\nTip: run "python manage.py showmigrations products" from backend/ to check migration status')
