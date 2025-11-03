from django.contrib.auth.models import User

KEEP = 'Bintou'

qs = User.objects.filter(is_superuser=True).exclude(username=KEEP)
if not qs.exists():
    print('No other superusers to delete.')
else:
    for u in qs:
        print('Deleting superuser:', u.username, 'id=', u.id)
        u.delete()

print('\nRemaining superusers:')
for u in User.objects.filter(is_superuser=True):
    print(u.id, u.username, u.email)
