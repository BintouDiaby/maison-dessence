from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.models import User


from django.contrib.auth.models import User, Group
from rest_framework import serializers
from django.conf import settings

VENDOR_GROUP_NAME = "vendor"

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    # champs pour déclarer un vendeur à l’inscription
    is_vendor = serializers.BooleanField(default=False)
    shop_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name',
                  'is_vendor', 'shop_name')

    def create(self, validated_data):
        is_vendor = validated_data.pop('is_vendor', False)
        shop_name = (validated_data.pop('shop_name', '') or '').strip()

        user = User(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        user.set_password(validated_data['password'])

        # ⚠️ Pour les tests: active direct en DEBUG, sinon garde l’email de vérif.
        user.is_active = True if getattr(settings, 'DEBUG', False) else False
        user.save()

        # Ajouter au groupe "client" par défaut (optionnel, déjà fait côté view)
        client_group, _ = Group.objects.get_or_create(name='client')
        user.groups.add(client_group)

        if is_vendor:
            vendor_group, _ = Group.objects.get_or_create(name=VENDOR_GROUP_NAME)
            user.groups.add(vendor_group)
            # Si tu as VendorProfile, on le renseigne:
            try:
                from .models import VendorProfile
                VendorProfile.objects.get_or_create(
                    user=user,
                    defaults={"shop_name": shop_name or f"Boutique de {user.username}"}
                )
            except Exception:
                pass

        return user



class ProfileSerializer(serializers.Serializer):
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    preferences = serializers.JSONField(required=False)

    def update(self, instance, validated_data):
        # instance is a Django User
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()
        # update profile preferences if exists
        try:
            profile = instance.profile
            prefs = validated_data.get('preferences')
            if prefs is not None:
                profile.preferences = prefs
                profile.save()
        except Exception:
            pass
        return instance


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Allow obtaining JWT using email + password in addition to username."""

    # Accept an `email` field in the request so DRF field validation doesn't
    # reject requests that post {"email": ..., "password": ...}.
    email = serializers.EmailField(required=False, write_only=True)
    username_field = 'username'

    def __init__(self, *args, **kwargs):
        # Make the username field optional so requests that supply only
        # an `email` + `password` don't fail field validation.
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            self.fields['username'].required = False

    def validate(self, attrs):
        # Accept either 'username' or 'email' as credential field
        username = attrs.get('username') or attrs.get('email')
        password = attrs.get('password')

        if username and '@' in username and 'email' not in attrs:
            # user provided email in the username field; normalize
            attrs['email'] = username

        # If email provided, try to resolve to username. Handle duplicates gracefully.
        email = attrs.get('email')
        if email and not attrs.get('username'):
            users = User.objects.filter(email__iexact=email)
            if not users.exists():
                # keep username blank; authentication will fail below
                attrs['username'] = ''
            else:
                # Prefer an active user if present, otherwise pick the most recently joined user
                user = users.filter(is_active=True).order_by('-date_joined').first() or users.order_by('-date_joined').first()
                attrs['username'] = user.username

        return super().validate(attrs)
