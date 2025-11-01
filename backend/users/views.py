from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from uuid import uuid4

from .serializers import RegisterSerializer, ProfileSerializer
from .serializers import EmailTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import EmailVerificationToken, PasswordResetToken, Profile
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
import logging

logger = logging.getLogger(__name__)


class ChangePasswordView(APIView):
	"""Allow authenticated users to change their password.

	Request: POST { "old_password": "..", "new_password": ".." }
	"""
	permission_classes = [IsAuthenticated]

	def post(self, request):
		user = request.user
		old = request.data.get('old_password')
		new = request.data.get('new_password')
		if not new or len(new) < 8:
			return Response({'detail': 'new_password is required and must be at least 8 chars'}, status=400)
		# If old password provided, verify it. If not provided, refuse for security.
		if not old:
			return Response({'detail': 'old_password is required'}, status=400)
		if not user.check_password(old):
			return Response({'detail': 'old password incorrect'}, status=400)
		user.set_password(new)
		user.save()
		return Response({'detail': 'password_changed'})


class RegisterAPIView(generics.CreateAPIView):
	serializer_class = RegisterSerializer

	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.save()

		# Ensure 'client' group exists and add user
		group, _ = Group.objects.get_or_create(name='client')
		user.groups.add(group)

		# Create an email verification token and send the verification link
		try:
			ev = EmailVerificationToken.objects.create(user=user)
			verify_url = f"{request.scheme}://{request.get_host()}/api/auth/verify-email/?token={ev.token}"
			subject = 'Vérifiez votre adresse e-mail pour Maison d\'essence'
			message = f"Bonjour {user.username},\n\nMerci pour votre inscription. Cliquez sur le lien suivant pour activer votre compte:\n\n{verify_url}\n\nSi vous n'avez pas demandé cette inscription, ignorez ce message.\n\nCordialement,\nMaison d'essence"
			from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
			send_mail(subject, message, from_email, [user.email], fail_silently=False)
		except Exception:
			logger.exception('Failed to create/send email verification token for user %s', getattr(user, 'id', None))

		return Response({'id': user.id, 'username': user.username, 'detail': 'verification_sent'}, status=status.HTTP_201_CREATED)


class VerifyEmailView(APIView):
	def get(self, request):
		token = request.GET.get('token')
		if not token:
			return Response({'detail': 'Token required'}, status=status.HTTP_400_BAD_REQUEST)
		try:
			ev = EmailVerificationToken.objects.get(token=token, used=False)
		except EmailVerificationToken.DoesNotExist:
			return Response({'detail': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
		ev.used = True
		ev.verified_at = timezone.now()
		ev.save()
		user = ev.user
		user.is_active = True
		user.save()
		return Response({'detail': 'Email verified'})


class PasswordResetRequestView(APIView):
	def post(self, request):
		email = request.data.get('email')
		if not email:
			return Response({'detail': 'Email required'}, status=status.HTTP_400_BAD_REQUEST)
		try:
			user = User.objects.get(email=email)
		except User.DoesNotExist:
			# don't reveal
			return Response({'detail': 'If the email exists, a reset link was sent.'})
		token = PasswordResetToken.objects.create(user=user)
		reset_url = f"{request.scheme}://{request.get_host()}/api/auth/password-reset/confirm/?token={token.token}"
		send_mail(
			subject='Password reset',
			message=f'Use this link to reset your password: {reset_url}',
			from_email=None,
			recipient_list=[user.email],
		)
		return Response({'detail': 'If the email exists, a reset link was sent.'})


class PasswordResetConfirmView(APIView):
	def post(self, request):
		token = request.data.get('token')
		new_password = request.data.get('new_password')
		if not token or not new_password:
			return Response({'detail': 'Token and new_password required'}, status=status.HTTP_400_BAD_REQUEST)
		try:
			pr = PasswordResetToken.objects.get(token=token, used=False)
		except PasswordResetToken.DoesNotExist:
			return Response({'detail': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
		user = pr.user
		user.set_password(new_password)
		user.save()
		pr.used = True
		pr.used_at = timezone.now()
		pr.save()
		return Response({'detail': 'Password updated'})


class ProfileView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		serializer = ProfileSerializer(request.user)
		return Response(serializer.data)

	def put(self, request):
		serializer = ProfileSerializer(instance=request.user, data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.save()
		return Response(ProfileSerializer(user).data)


class EmailTokenObtainPairView(TokenObtainPairView):
    """Issue JWT tokens using email+password or username+password."""
    serializer_class = EmailTokenObtainPairSerializer


class ImpersonateUserView(APIView):
	"""Allow a superuser to obtain JWT tokens for another user (impersonation).

	Security: only `is_superuser` is allowed. The endpoint returns access and
	refresh tokens for the target user and logs the action. The client is
	expected to store original admin tokens (if any) before switching.
	"""
	permission_classes = [IsAuthenticated]

	def post(self, request):
		# Accept either user id or email or username
		user_id = request.data.get('user_id')
		email = request.data.get('email')
		username = request.data.get('username')

		target = None
		try:
			if user_id:
				target = User.objects.get(id=int(user_id))
			elif email:
				target = User.objects.get(email=email)
			elif username:
				target = User.objects.get(username=username)
			else:
				return Response({'detail': 'user_id, email or username required'}, status=400)
		except User.DoesNotExist:
			return Response({'detail': 'User not found'}, status=404)

		# Only allow actual superusers to call this endpoint
		if not request.user.is_superuser:
			return Response({'detail': 'Only superusers may impersonate other users'}, status=403)

		# Prevent impersonating other superusers by default
		if target.is_superuser:
			return Response({'detail': 'Impersonating other superusers is not allowed'}, status=403)

		# create tokens for target user
		refresh = RefreshToken.for_user(target)
		access = str(refresh.access_token)
		refresh_str = str(refresh)

		logger.info('User %s (id=%s) impersonated user %s (id=%s)', request.user.username, request.user.id, target.username, target.id)

		return Response({
			'access': access,
			'refresh': refresh_str,
			'user': {
				'id': target.id,
				'username': target.username,
				'email': target.email,
				'is_staff': target.is_staff,
				'is_superuser': target.is_superuser,
			}
		})

