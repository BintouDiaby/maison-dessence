import os
import sys
import json
from decimal import Decimal

# Run from backend/ as working dir
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from products.models import Product

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'products', 'data', 'products.json')
DATA_FILE = os.path.normpath(DATA_FILE)

print('Reading', DATA_FILE)
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

created = 0
skipped = 0
for item in data:
    name = (item.get('name') or '').strip()
    if not name:
        print('Skipping entry with no name:', item)
        skipped += 1
        continue
    # Detect duplicates by name
    exists = Product.objects.filter(name__iexact=name).exists()
    if exists:
        print('Already exists, skipping:', name)
        skipped += 1
        continue

    price = item.get('price')
    try:
        price = Decimal(str(price)) if price is not None else None
    except Exception:
        price = None

    p = Product(
        owner=None,
        name=name,
        description=item.get('description') or '',
        price=price or Decimal('0.00'),
        stock=int(item.get('stock') or 0),
        family=item.get('family') or '',
        concentration=item.get('concentration') or '',
        image_url=item.get('image_url') or '',
        tags=item.get('tags') or []
    )
    p.save()
    created += 1
    print('Created product:', p.id, p.name)

print('\nImport complete. Created:', created, 'Skipped:', skipped)
