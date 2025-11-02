from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    owner_shop = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'owner', 'name', 'description', 'price', 'stock',
            'family', 'concentration', 'image_url', 'image', 'tags', 'owner_shop'
        ]

    def get_owner_shop(self, obj):
        try:
            owner = getattr(obj, 'owner', None) or getattr(obj, 'user', None)
            vp = getattr(owner, 'vendor_profile', None) if owner is not None else None
            if vp and getattr(vp, 'shop_name', None):
                return vp.shop_name
            # fallback to a sensible default using owner's username
            if owner and getattr(owner, 'username', None):
                return f"Boutique de {owner.username}"
        except Exception:
            pass
        return None
