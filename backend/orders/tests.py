from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Cart, CartItem


class CartIntegrationTests(TestCase):
	def setUp(self):
		User = get_user_model()
		self.user = User.objects.create_user(username='cartuser', password='pass')

	def test_cart_total_and_items_list(self):
		# create cart for user
		cart = Cart.objects.create(user=self.user)
		# add items
		CartItem.objects.create(cart=cart, product_id=1, quantity=2, unit_price='5.00')
		CartItem.objects.create(cart=cart, product_id=2, quantity=1, unit_price='3.50')

		total = cart.total()
		# 2*5.00 + 1*3.50 = 13.50
		self.assertEqual(str(total), '13.50')

		items = cart.items_list()
		self.assertEqual(len(items), 2)

