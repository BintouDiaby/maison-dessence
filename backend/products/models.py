from django.db import models
from django.conf import settings  # IMPORTANT

class Product(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='products',
        null=True, blank=True,  # temporaire pour migration douce
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.IntegerField(default=0)
    family = models.CharField(max_length=100, blank=True)
    concentration = models.CharField(max_length=100, blank=True)
    image_url = models.CharField(max_length=1024, blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    tags = models.JSONField(default=list, blank=True)
    # Users who liked this product
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_products',
        blank=True,
    )
    # Users who added this product to their wishlist
    wishlisted_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='wishlist_products',
        blank=True,
    )

    def __str__(self):
        return f"{self.name} ({self.id})"

    class Meta:
        ordering = ['id']

    @property
    def image_display_url(self) -> str:
        if self.image and hasattr(self.image, 'url'):
            return str(self.image.url)
        return self.image_url or ''
