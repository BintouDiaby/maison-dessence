from rest_framework import permissions
from django.contrib.auth.models import Group

VENDOR_GROUP_NAME = "vendor"

def user_is_vendor(user) -> bool:
    return user.is_authenticated and user.groups.filter(name=VENDOR_GROUP_NAME).exists()

class IsVendor(permissions.BasePermission):
    """
    Autorise l'écriture si l'utilisateur est vendeur.
    Lecture publique autorisée.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return user_is_vendor(request.user)

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Autorise la modification uniquement au propriétaire du produit.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(obj, "owner_id", None) == getattr(request.user, "id", None)
