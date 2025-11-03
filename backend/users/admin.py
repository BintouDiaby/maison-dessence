from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User

from .models import Profile, EmailVerificationToken, PasswordResetToken
from .models import VendorProfile, VENDOR_GROUP_NAME


class ProfileInline(admin.StackedInline):
	model = Profile
	can_delete = False
	verbose_name_plural = 'profile'


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
	list_display = ('user', 'token', 'used', 'created_at')
	search_fields = ('user__username', 'user__email', 'token')


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
	list_display = ('user', 'token', 'used', 'created_at')
	search_fields = ('user__username', 'user__email', 'token')


class UserAdmin(DjangoUserAdmin):
	inlines = (ProfileInline,)
	list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_client', 'is_vendor')
	list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
	actions = ['activate_users', 'deactivate_users']

	def activate_users(self, request, queryset):
		updated = queryset.update(is_active=True)
		self.message_user(request, f"{updated} utilisateur(s) activé(s).")

	activate_users.short_description = 'Activer les utilisateurs sélectionnés'

	def deactivate_users(self, request, queryset):
		updated = queryset.update(is_active=False)
		self.message_user(request, f"{updated} utilisateur(s) désactivé(s).")

	deactivate_users.short_description = 'Désactiver les utilisateurs sélectionnés'

	def is_client(self, obj):
		"""Return True if the user is member of the 'client' group."""
		try:
			return obj.groups.filter(name='client').exists()
		except Exception:
			return False

	is_client.boolean = True
	is_client.short_description = 'Client'

	def is_vendor(self, obj):
		"""Return True if the user is member of the 'vendor' group."""
		try:
			return obj.groups.filter(name=VENDOR_GROUP_NAME).exists()
		except Exception:
			return False

	is_vendor.boolean = True
	is_vendor.short_description = 'Vendeur'


# Re-register User admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'shop_name', 'verified')
	search_fields = ('user__username', 'user__email', 'shop_name')
	list_filter = ('verified',)

