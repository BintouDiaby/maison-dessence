from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone


class Interaction(models.Model):
	EVENT_CHOICES = [
		('view', 'View'),
		('click', 'Click'),
		('add_to_cart', 'Add to cart'),
		('purchase', 'Purchase'),
	]

	user = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL)
	product_id = models.IntegerField()
	event_type = models.CharField(max_length=32, choices=EVENT_CHOICES)
	value = models.FloatField(null=True, blank=True)
	metadata = models.JSONField(default=dict, blank=True)
	created_at = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return f"Interaction {self.event_type} user={self.user_id} product={self.product_id}"
