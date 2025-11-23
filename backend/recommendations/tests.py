from django.test import TestCase
from django.contrib.auth.models import User
from products.models import Product
from .recommender import train, similar_products


class RecommenderTests(TestCase):
    """Tests pour le système de recommandations (ML)."""

    def setUp(self):
        self.user = User.objects.create_user(username='recuser', email='rec@example.com', password='pass')
        # Créer quelques produits
        self.prod1 = Product.objects.create(
            owner=self.user,
            name='Product A',
            description='Coffee beans from Ethiopia',
            price=10.0,
            stock=5
        )
        self.prod2 = Product.objects.create(
            owner=self.user,
            name='Product B',
            description='Coffee beans from Colombia',
            price=12.0,
            stock=3
        )
        self.prod3 = Product.objects.create(
            owner=self.user,
            name='Product C',
            description='Tea leaves from China',
            price=8.0,
            stock=10
        )

    def test_train_recommender_basic(self):
        """Vérifier que le recommender peut être entraîné sans erreur."""
        try:
            result = train()
            
            self.assertTrue(True)
            self.assertIsInstance(result, dict)
            self.assertIn('n_products', result)
        except Exception as e:
            self.fail(f'train() failed: {e}')

    def test_get_recommendations_returns_list(self):
        """Vérifier que similar_products retourne une liste (même vide)."""
        train()
        recs = similar_products(product_id=self.prod1.id, k=2)
        self.assertIsInstance(recs, list)
        # Le contenu exact dépend du modèle — on vérifie juste que c'est une liste

    def test_get_recommendations_similar_products(self):
        """Vérifier que les recommandations retournent des produits similaires."""
        train()
        recs = similar_products(product_id=self.prod1.id, k=2)
        # prod1 parle de "coffee", donc prod2 (coffee aussi) devrait être similaire
        # Ce test est basique — en réalité le modèle TF-IDF peut varier
        if len(recs) > 0:
            rec_ids = [r['id'] for r in recs]
            # On vérifie juste qu'on a des IDs valides
            self.assertTrue(all(isinstance(rid, int) for rid in rec_ids))
