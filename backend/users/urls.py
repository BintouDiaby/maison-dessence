# backend/users/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterAPIView,
    VerifyEmailView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    ProfileView,
    EmailTokenObtainPairSerializer,   # <- pas une vue
    EmailTokenObtainPairView,          # <- la bonne vue
    ChangePasswordView,
    ImpersonateUserView,
    vendor_me,          # GET (et on va te donner un upgrade dédié juste après)
    vendor_upgrade,     # NEW: POST pour passer vendeur
    # endpoint to create a Django session from JWT for admin access
    
)

urlpatterns = [
    # Auth de base
    path('auth/register/', RegisterAPIView.as_view(), name='auth-register'),
    path('auth/token/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/verify-email/', VerifyEmailView.as_view(), name='auth-verify-email'),
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='auth-password-reset'),
    path('auth/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='auth-password-reset-confirm'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='auth-change-password'),
    path('auth/profile/', ProfileView.as_view(), name='auth-profile'),
    path('auth/impersonate/', ImpersonateUserView.as_view(), name='auth-impersonate'),

    # Vendeur
    path('vendors/me/', vendor_me, name='vendor_me'),             # GET: état vendeur
    path('vendors/upgrade/', vendor_upgrade, name='vendor_upgrade'),  # POST: devenir vendeur
]
