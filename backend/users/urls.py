from django.urls import path
from .views import RegisterAPIView, VerifyEmailView, PasswordResetRequestView, PasswordResetConfirmView, ProfileView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from .views import EmailTokenObtainPairView
from .views import ChangePasswordView
from .views import ImpersonateUserView

urlpatterns = [
    path('auth/register/', RegisterAPIView.as_view(), name='auth-register'),
    path('auth/token/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/verify-email/', VerifyEmailView.as_view(), name='auth-verify-email'),
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='auth-password-reset'),
    path('auth/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='auth-password-reset-confirm'),
    path('auth/profile/', ProfileView.as_view(), name='auth-profile'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='auth-change-password'),
    path('auth/impersonate/', ImpersonateUserView.as_view(), name='auth-impersonate'),
]

