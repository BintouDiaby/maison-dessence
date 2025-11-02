from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


def _generate_token():
	return uuid.uuid4().hex


class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
	preferences = models.JSONField(default=dict, blank=True)
	history = models.JSONField(default=list, blank=True)

	def __str__(self):
		return f"Profile({self.user.username})"


class EmailVerificationToken(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	token = models.CharField(max_length=64, default=_generate_token, unique=True)
	created_at = models.DateTimeField(auto_now_add=True)
	used = models.BooleanField(default=False)
	verified_at = models.DateTimeField(null=True, blank=True)

	def __str__(self):
		return f"EmailVerificationToken({self.user.username}, used={self.used})"


class PasswordResetToken(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	token = models.CharField(max_length=64, default=_generate_token, unique=True)
	created_at = models.DateTimeField(auto_now_add=True)
	used = models.BooleanField(default=False)
	used_at = models.DateTimeField(null=True, blank=True)

	def __str__(self):
		return f"PasswordResetToken({self.user.username}, used={self.used})"


from django.db.models.signals import post_save
from django.dispatch import receiver


from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import Group

@receiver(post_save, sender=User)
def create_profile_and_assign_group(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        # ensure client group exists
        client_group, _ = Group.objects.get_or_create(name='client')
        instance.groups.add(client_group)
        # s'assurer que le groupe vendor existe (pas d’ajout par défaut)
        ensure_vendor_group_exists()

@receiver(m2m_changed, sender=User.groups.through)
def ensure_vendor_profile_on_group_add(sender, instance: User, action, pk_set, **kwargs):
    """
    Quand on ajoute le groupe 'vendor' à un utilisateur, crée le VendorProfile s'il n'existe pas.
    """
    if action == "post_add" and pk_set:
        try:
            vendor_group = Group.objects.get(name=VENDOR_GROUP_NAME)
        except Group.DoesNotExist:
            return
        if vendor_group.pk in pk_set and not hasattr(instance, "vendor_profile"):
            VendorProfile.objects.create(
                user=instance,
                shop_name=f"Boutique de {instance.username}"
            )

# === VENDOR SUPPORT ===
from django.contrib.auth.models import Group

VENDOR_GROUP_NAME = "vendor"

class VendorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="vendor_profile")
    shop_name = models.CharField(max_length=150)
    bio = models.TextField(blank=True)
    logo = models.ImageField(upload_to="vendors/", null=True, blank=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.shop_name} ({self.user.username})"


def ensure_vendor_group_exists():
    Group.objects.get_or_create(name=VENDOR_GROUP_NAME)


def user_is_vendor(user: User) -> bool:
    return user.is_authenticated and user.groups.filter(name=VENDOR_GROUP_NAME).exists()
