from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Product


class ProductModelTests(TestCase):
	def setUp(self):
		User = get_user_model()
		self.user = User.objects.create_user(username='tester', password='pass')

	def test_create_product_and_str(self):
		p = Product.objects.create(
			owner=self.user,
			name='Lavender Oil',
			description='Nice scent',
			price='12.50',
			stock=10,
			image_url='http://example.com/img.png'
		)
		self.assertIn('Lavender Oil', str(p))

	def test_image_display_url_prefers_image_field_or_image_url(self):
		p = Product.objects.create(
			owner=self.user,
			name='Test',
			price='1.00',
			stock=1,
			image_url='http://example.com/fallback.png'
		)
		# No image file attached - use image_url
		self.assertEqual(p.image_display_url, 'http://example.com/fallback.png')

	def test_likes_and_wishlist(self):
		p = Product.objects.create(
			owner=self.user,
			name='Likeable',
			price='3.00',
			stock=5,
		)
		# initially no likes
		self.assertEqual(p.likes.count(), 0)
		self.assertEqual(p.wishlisted_by.count(), 0)

		# add like and wishlist
		p.likes.add(self.user)
		p.wishlisted_by.add(self.user)
		self.assertTrue(p.likes.filter(id=self.user.id).exists())
		self.assertTrue(p.wishlisted_by.filter(id=self.user.id).exists())

