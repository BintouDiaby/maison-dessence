from django.test import TestCase
from django.contrib.auth.models import User
from .models import Interaction


class InteractionModelTests(TestCase):
    """Tests unitaires pour le modèle Interaction."""

    def setUp(self):
        self.user = User.objects.create_user(username='interactuser', email='interact@example.com', password='pass')

    def test_create_interaction_view(self):
        """Créer une interaction de type 'view'."""
        interaction = Interaction.objects.create(
            user=self.user,
            product_id=1,
            event_type='view'
        )
        self.assertEqual(interaction.event_type, 'view')
        self.assertEqual(interaction.product_id, 1)
        self.assertEqual(interaction.user, self.user)

    def test_create_interaction_purchase(self):
        """Créer une interaction de type 'purchase' avec valeur."""
        interaction = Interaction.objects.create(
            user=self.user,
            product_id=42,
            event_type='purchase',
            value=99.99
        )
        self.assertEqual(interaction.event_type, 'purchase')
        self.assertEqual(interaction.value, 99.99)

    def test_interaction_str(self):
        """Vérifier la représentation string."""
        interaction = Interaction.objects.create(
            user=self.user,
            product_id=10,
            event_type='click'
        )
        self.assertIn('click', str(interaction))
        self.assertIn('10', str(interaction))
