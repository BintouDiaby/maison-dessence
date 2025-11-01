from django.db import models
from django.contrib.postgres.fields import ArrayField


class Product(models.Model):
	name = models.CharField(max_length=255)
	description = models.TextField(blank=True)
	price = models.DecimalField(max_digits=8, decimal_places=2)
	stock = models.IntegerField(default=0)
	family = models.CharField(max_length=100, blank=True)
	concentration = models.CharField(max_length=100, blank=True)
	image_url = models.CharField(max_length=1024, blank=True)
	# ImageField used for uploaded product photos via the admin interface.
	# Keep `image_url` as a fallback for externally hosted images already in the DB.
	image = models.ImageField(upload_to='products/', blank=True, null=True)
	# tags as a simple comma separated list for sqlite fallback; use JSON/Array in Postgres
	tags = models.JSONField(default=list, blank=True)

	def __str__(self):
		return f"{self.name} ({self.id})"

	class Meta:
		ordering = ['id']

	@property
	def image_display_url(self) -> str:
		"""Return the URL for the product image, preferring uploaded file over legacy image_url."""
		if self.image and hasattr(self.image, 'url'):
			return str(self.image.url)
		return self.image_url or ''
