import os
import sys
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()
from django.core.management import call_command

print('Running makemigrations for products...')
call_command('makemigrations', 'products')
print('Running migrate...')
call_command('migrate')
print('Migrations complete')
