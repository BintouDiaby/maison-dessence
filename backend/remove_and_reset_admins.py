import os
import sys
import secrets
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()

# Safety: ensure there are at least two admin candidates before deleting one of them
admins = list(User.objects.filter(is_superuser=True).order_by('id'))
print('Current superusers:', [(u.id, u.username) for u in admins])

username_to_remove = 'Bintou'  # target duplicate to demote+delete
try:
    u = User.objects.get(username=username_to_remove)
except User.DoesNotExist:
    print(f"User {username_to_remove} not found. Aborting deletion.")
    u = None

# Ensure there will remain at least one superuser after deletion/demotion
remaining_admins = [a for a in admins if a.username != username_to_remove]
if u:
    if u.is_superuser or u.is_staff:
        if not remaining_admins:
            print('Refusing to delete the last superuser. Aborting.')
        else:
            # Demote first (safety) then delete
            print(f"Demoting user {u.username} (id={u.id})...")
            u.is_superuser = False
            u.is_staff = False
            u.save()
            print('Demoted. Now deleting...')
            u.delete()
            print(f"Deleted user {username_to_remove}.")
    else:
        print(f"User {username_to_remove} exists but is not staff/superuser; deleting directly.")
        u.delete()
        print(f"Deleted user {username_to_remove}.")

# Now reset passwords for remaining admin accounts (is_superuser or is_staff)
admins_after = list(User.objects.filter(is_staff=True).order_by('id'))
print('Admin accounts to reset passwords for:', [(a.id, a.username) for a in admins_after])
new_passwords = {}
for a in admins_after:
    pw = secrets.token_urlsafe(10)
    a.set_password(pw)
    a.is_active = True
    # ensure they remain admin
    a.is_staff = True
    a.is_superuser = True
    a.save()
    new_passwords[a.username] = pw

print('\nNew passwords for admin accounts:')
for username, pw in new_passwords.items():
    print(f"- {username}: {pw}")

print('\nOperation completed. Please store these passwords securely and change them on first login.')
