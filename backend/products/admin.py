from django.contrib import admin
from django.utils.html import format_html
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	"""Admin for Product: show image preview and allow editing/uploading images."""
	list_display = ("id", "name", "price", "stock", "family", "image_tag", "edit_link")
	search_fields = ("name", "description", "family", "tags")
	list_filter = ("family",)
	ordering = ("-id",)
	readonly_fields = ("image_tag",)
	list_display_links = ("name",)
	list_per_page = 50
	actions = ["action_edit_first_selected", "import_products_from_json_action"]

	fieldsets = (
		(None, {
			'fields': ('name', 'description', 'price', 'stock', 'family', 'concentration', 'tags')
		}),
		('Image', {
			'fields': ('image', 'image_url', 'image_tag'),
			'description': 'Upload an image file or set an external image_url. Uploaded image is preferred.'
		}),
	)

	def image_tag(self, obj):
		if obj and getattr(obj, 'image') and getattr(obj.image, 'url', None):
			return format_html('<img src="{}" style="height:60px;"/>', obj.image.url)
		if obj and getattr(obj, 'image_url', None):
			return format_html('<img src="{}" style="height:60px;"/>', obj.image_url)
		return ""

	image_tag.short_description = 'Image'

	def edit_link(self, obj):
		from django.urls import reverse
		if not obj:
			return ""
		url = reverse('admin:products_product_change', args=(obj.pk,))
		return format_html('<a href="{}">Edit</a>', url)

	edit_link.short_description = 'Edit'

	def action_edit_first_selected(self, request, queryset):
		"""Admin action: redirect to the change page for the first selected product."""
		from django.http import HttpResponseRedirect
		from django.urls import reverse

		first = queryset.first()
		if not first:
			self.message_user(request, "No product selected.")
			return
		url = reverse('admin:products_product_change', args=(first.pk,))
		return HttpResponseRedirect(url)

	action_edit_first_selected.short_description = 'Edit first selected product'

	def import_products_from_json_action(self, request, queryset):
		"""Admin action: import products from products/data/products.json into the DB.
		This is non-destructive and will skip existing products by case-insensitive name match.
		You can run it from the products changelist (select any or none) and then choose the action.
		"""
		from django.contrib import messages
		import os, json
		from decimal import Decimal

		data_file = os.path.join(os.path.dirname(__file__), 'data', 'products.json')
		if not os.path.exists(data_file):
			self.message_user(request, f'products.json not found at {data_file}', level=messages.ERROR)
			return

		created = 0
		skipped = 0
		with open(data_file, 'r', encoding='utf-8') as f:
			items = json.load(f)

		for item in items:
			name = (item.get('name') or '').strip()
			if not name:
				skipped += 1
				continue
			if Product.objects.filter(name__iexact=name).exists():
				skipped += 1
				continue
			price = item.get('price')
			try:
				price = Decimal(str(price)) if price is not None else None
			except Exception:
				price = None

			p = Product(
				owner=None,
				name=name,
				description=item.get('description') or '',
				price=price or Decimal('0.00'),
				stock=int(item.get('stock') or 0),
				family=item.get('family') or '',
				concentration=item.get('concentration') or '',
				image_url=item.get('image_url') or '',
				tags=item.get('tags') or []
			)
			p.save()
			created += 1

		self.message_user(request, f'Import complete. Created: {created} — Skipped: {skipped}', level=messages.INFO)

	import_products_from_json_action.short_description = 'Importer produits depuis products.json'

# If you prefer the older style, you can also do:
# admin.site.register(Product, ProductAdmin)
