from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User

from .models import Profile, EmailVerificationToken, PasswordResetToken


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
	list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_client')
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


# Re-register User admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

