# d:\Projets\maison-dessence\backend\create_test_user.py
# Script pour créer un utilisateur de test
# USAGE: python create_test_user.py
# RELEVANT FILES: backend/users/models.py, backend/users/views.py

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Créer plusieurs utilisateurs de test
users_to_create = [
    {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123',
        'is_staff': False
    },
    {
        'username': 'admin',
        'email': 'admin@example.com',
        'password': 'admin123',
        'is_staff': True,
        'is_superuser': True
    },
    {
        'username': 'vendor',
        'email': 'vendor@example.com',
        'password': 'vendor123',
        'is_staff': False
    }
]

print("\n=== Création des Utilisateurs de Test ===\n")

for user_data in users_to_create:
    username = user_data['username']
    email = user_data['email']
    password = user_data['password']
    
    # Vérifier si l'utilisateur existe déjà
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        user.set_password(password)
        user.email = email
        user.is_staff = user_data.get('is_staff', False)
        user.is_superuser = user_data.get('is_superuser', False)
        user.save()
        print(f"✅ User mis à jour: {username}")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
    else:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.is_staff = user_data.get('is_staff', False)
        user.is_superuser = user_data.get('is_superuser', False)
        user.save()
        print(f"✅ User créé: {username}")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
    
    print()

print("\n=== Résumé ===")
print(f"Total utilisateurs: {User.objects.count()}")
print("\n💡 Teste maintenant le login dans Thunder Client:")
print("   URL: POST http://localhost:8000/api/auth/token/")
print("   Body (JSON):")
print('   {"email": "test@example.com", "password": "testpass123"}')
print("\n   OU:")
print('   {"username": "testuser", "password": "testpass123"}')
print()
