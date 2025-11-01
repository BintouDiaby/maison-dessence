from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone


class Order(models.Model):
	STATUS_CHOICES = [
		('pending', 'Pending'),
		('paid', 'Paid'),
		('shipped', 'Shipped'),
		('cancelled', 'Cancelled'),
	]

	user = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL)
	items = models.JSONField(default=list)  # list of {product_id, quantity, price}
	total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
	created_at = models.DateTimeField(default=timezone.now)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"Order #{self.id} - {self.status} - {self.total}"


class Cart(models.Model):
	"""Simple cart tied to a user (one active cart per user)."""
	user = models.OneToOneField(get_user_model(), null=True, blank=True, on_delete=models.CASCADE, related_name='cart')
	created_at = models.DateTimeField(default=timezone.now)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"Cart({self.user})"

	def items_list(self):
		# Return a serializable list of items
		return [ci.as_dict() for ci in self.items.all()]

	def total(self):
		from decimal import Decimal

		total = Decimal('0')
		for ci in self.items.all():
			total += ci.unit_price * ci.quantity
		return total


class CartItem(models.Model):
	cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
	product_id = models.IntegerField()  # reference to products.Product.id
	quantity = models.PositiveIntegerField(default=1)
	unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

	class Meta:
		unique_together = ('cart', 'product_id')

	def __str__(self):
		return f"CartItem(product={self.product_id}, qty={self.quantity})"

	def as_dict(self):
		return {
			'product_id': self.product_id,
			'quantity': self.quantity,
			'unit_price': str(self.unit_price),
			'total_price': str(self.unit_price * self.quantity)
		}
