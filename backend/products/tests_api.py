# Header comments
# File: backend/products/tests_api.py
# Description: Tests fonctionnels pour les endpoints API produits (création, permissions, like, wishlist)
# WHY: couvrir les principaux flux API pour démonstration et CI
# RELEVANT FILES: backend/products/views.py, backend/products/urls.py, backend/products/models.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APIClient

from products.models import Product


class ProductsAPITests(TestCase):
    """Tests fonctionnels (API) pour les endpoints produits.

    - create: accessible uniquement aux utilisateurs du groupe 'vendor'
    - like/wishlist: toggles par utilisateur authentifié
    - my_wishlist: retourne les produits de l'utilisateur
    """

    def setUp(self):
        User = get_user_model()
        self.client = APIClient()
        # créer deux utilisateurs : vendor et normal
        self.vendor = User.objects.create_user(username='vendor_user', password='pass')
        self.user = User.objects.create_user(username='normal_user', password='pass')
        Group.objects.get_or_create(name='vendor')
        vendor_group = Group.objects.get(name='vendor')
        vendor_group.user_set.add(self.vendor)

    def test_create_product_as_vendor(self):
        self.client.force_authenticate(user=self.vendor)
        payload = {'name': 'APITest Product', 'price': '9.99', 'stock': 5}
        resp = self.client.post('/api/products/create/', payload, format='json')
        self.assertEqual(resp.status_code, 201, msg=f'Unexpected response: {resp.status_code} {resp.data}')
        data = resp.data
        self.assertEqual(data.get('name'), 'APITest Product')
        # vérifier que le produit est bien créé et appartient au vendor
        p = Product.objects.get(pk=data.get('id'))
        self.assertEqual(p.owner, self.vendor)

    def test_create_product_forbidden_for_non_vendor(self):
        self.client.force_authenticate(user=self.user)
        payload = {'name': 'NotAllowed', 'price': '1.00'}
        resp = self.client.post('/api/products/create/', payload, format='json')
        self.assertEqual(resp.status_code, 403)

    def test_like_and_wishlist_toggle_and_my_wishlist(self):
        # vendor crée un produit
        p = Product.objects.create(owner=self.vendor, name='ToggleProd', price=1.5, stock=10)

        # utilisateur normal aime le produit
        self.client.force_authenticate(user=self.user)
        resp = self.client.post(f'/api/products/{p.pk}/like/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data.get('liked'))
        self.assertEqual(resp.data.get('likes_count'), 1)

        # toggle unlike
        resp = self.client.post(f'/api/products/{p.pk}/like/')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.data.get('liked'))
        self.assertEqual(resp.data.get('likes_count'), 0)

        # wishlist toggle
        resp = self.client.post(f'/api/products/{p.pk}/wishlist/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data.get('in_wishlist'))
        self.assertEqual(resp.data.get('wishlist_count'), 1)

        # my wishlist should include the product
        resp = self.client.get('/api/me/wishlist/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data.get('count'), 1)
        results = resp.data.get('results') or []
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], p.pk)
