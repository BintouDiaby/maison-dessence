from django.test import TestCase
from django.contrib.auth.models import User, Group
from rest_framework.test import APIClient
from rest_framework import status
from .models import Profile, EmailVerificationToken, PasswordResetToken


class UserModelTests(TestCase):
    """Tests unitaires pour les modèles User et Profile."""

    def test_create_user_and_profile(self):
        """Créer un user → le signal crée automatiquement un Profile."""
        user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsInstance(user.profile, Profile)
        self.assertEqual(user.profile.user, user)

    def test_email_verification_token_creation(self):
        """Vérifier qu'un token d'email peut être créé et utilisé."""
        user = User.objects.create_user(username='verifytest', email='verify@example.com', password='pass')
        token = EmailVerificationToken.objects.create(user=user)
        self.assertFalse(token.used)
        self.assertIsNotNone(token.token)
        self.assertEqual(len(token.token), 32)  # uuid hex = 32 chars

    def test_password_reset_token_creation(self):
        """Vérifier qu'un token de reset password peut être créé."""
        user = User.objects.create_user(username='resettest', email='reset@example.com', password='pass')
        token = PasswordResetToken.objects.create(user=user)
        self.assertFalse(token.used)
        self.assertIsNotNone(token.token)


class UserAPITests(TestCase):
    """Tests fonctionnels pour les endpoints liés aux users (signup, login, etc.)."""

    def setUp(self):
        self.client = APIClient()
        self.vendor_group, _ = Group.objects.get_or_create(name='vendor')

    def test_user_signup_creates_profile(self):
        """Tester qu'on peut créer un user via l'API (si endpoint existe)."""
        # Note: adapter selon votre endpoint réel de signup
        # Ici on teste juste la création directe en DB
        user = User.objects.create_user(username='apiuser', email='api@example.com', password='apipass')
        self.assertTrue(User.objects.filter(username='apiuser').exists())
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_vendor_group_assignment(self):
        """Vérifier qu'un user peut être assigné au groupe vendor."""
        user = User.objects.create_user(username='vendor1', email='vendor@example.com', password='vendorpass')
        user.groups.add(self.vendor_group)
        self.assertTrue(user.groups.filter(name='vendor').exists())
