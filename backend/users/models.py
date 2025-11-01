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


@receiver(post_save, sender=User)
def create_profile_and_assign_group(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)
		# ensure client group exists
		from django.contrib.auth.models import Group
		group, _ = Group.objects.get_or_create(name='client')
		instance.groups.add(group)
