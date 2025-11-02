import json
import os
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = 'Seed products from products/data/products.json into Product model.'

    def handle(self, *args, **options):
        from products.models import Product

        data_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'products.json')
        if not os.path.exists(data_file):
            self.stdout.write(self.style.ERROR(f"Products data file not found: {data_file}"))
            return

        with open(data_file, 'r', encoding='utf-8') as f:
            products = json.load(f)

        created = 0
        with transaction.atomic():
            for p in products:
                pid = p.get('id')
                obj, was_created = Product.objects.update_or_create(
                    id=pid,
                    defaults={
                        'name': p.get('name') or '',
                        'description': p.get('description') or '',
                        'price': p.get('price') or 0,
                        'stock': p.get('stock') or 0,
                        'family': p.get('family') or '',
                        'concentration': p.get('concentration') or '',
                        'image_url': p.get('image_url') or '',
                        'tags': p.get('tags') or [],
                    }
                )
                if was_created:
                    created += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded products (created {created}, total {len(products)})"))
