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
	actions = ["action_edit_first_selected"]

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

# If you prefer the older style, you can also do:
# admin.site.register(Product, ProductAdmin)
