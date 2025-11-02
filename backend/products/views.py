# backend/products/views.py
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_GET, require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from difflib import SequenceMatcher
from django.conf import settings
import json
import os
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
# Try to import Product model; if missing, we'll fall back to a JSON data file
try:
    from .models import Product  # type: ignore
    HAS_MODEL = True
except Exception:
    Product = None
    HAS_MODEL = False

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'products.json')
VENDOR_GROUP_NAME = "vendor"

def ensure_vendor_group_exists():
    Group.objects.get_or_create(name=VENDOR_GROUP_NAME)

def user_is_vendor(user) -> bool:
    return user.is_authenticated and user.groups.filter(name=VENDOR_GROUP_NAME).exists()

def _load_products_from_file():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except Exception:
        return []

def product_to_dict(p) -> dict:
    # p peut être une instance de modèle ou un dict (fallback JSON)
    if HAS_MODEL and hasattr(p, 'id'):
        return {
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': float(p.price) if getattr(p, 'price', None) is not None else None,
            'stock': getattr(p, 'stock', None),
            'family': getattr(p, 'family', None),
            'concentration': getattr(p, 'concentration', None),
            'image_url': (getattr(p, 'image', None).url if getattr(p, 'image', None) and getattr(p, 'image', None).name else getattr(p, 'image_url', None)),
            'tags': getattr(p, 'tags', []) or [],
            'owner': getattr(p.owner, 'username', None) if hasattr(p, 'owner') and p.owner else None,
        }
    else:
        return {
            'id': p.get('id'),
            'name': p.get('name'),
            'description': p.get('description'),
            'price': p.get('price'),
            'stock': p.get('stock'),
            'family': p.get('family'),
            'concentration': p.get('concentration'),
            'image_url': p.get('image_url'),
            'tags': p.get('tags', []),
            'owner': p.get('owner', None),
        }

@api_view(["GET"])
@authentication_classes([JWTAuthentication])   # JWT lu si présent (sinon user=Anonymous)
@permission_classes([AllowAny])                # lecture publique permise
def products_list(request):
    # Legacy: si aucun param, renvoyer une liste simple comme avant
    has_params = any(k in request.query_params for k in ('q', 'page', 'page_size', 'mine'))
    if not has_params:
        if HAS_MODEL:
            qs = Product.objects.all()
            data = [product_to_dict(p) for p in qs]
        else:
            data = _load_products_from_file()
        return Response(data, status=200)

    q = (request.query_params.get('q') or '').strip()
    mine = request.query_params.get('mine')
    try:
        page = max(1, int(request.query_params.get('page', '1')))
    except Exception:
        page = 1
    try:
        page_size = max(1, min(100, int(request.query_params.get('page_size', '20'))))
    except Exception:
        page_size = 20

    if HAS_MODEL:
        from django.db import models as dj_models
        qs = Product.objects.all()
        # 👉 maintenant, si tu passes le JWT, request.user sera bien renseigné
        if mine and request.user and request.user.is_authenticated:
            qs = qs.filter(owner=request.user)
        if q:
            qs = qs.filter(
                dj_models.Q(name__icontains=q) |
                dj_models.Q(description__icontains=q) |
                dj_models.Q(tags__icontains=q)
            )
        total = qs.count()
        start = (page - 1) * page_size
        end = start + page_size
        data = [product_to_dict(p) for p in qs.order_by('id')[start:end]]
    else:
        data = _load_products_from_file()
        if q:
            qlow = q.lower()
            data = [
                p for p in data
                if qlow in (p.get('name') or '').lower()
                or qlow in (p.get('description') or '').lower()
                or qlow in ' '.join(p.get('tags', [])).lower()
            ]
        # (fallback JSON : pas de notion d'owner)
        total = len(data)
        start = (page - 1) * page_size
        end = start + page_size
        data = data[start:end]

    return Response({'results': data, 'count': total, 'page': page, 'page_size': page_size}, status=200)
@require_GET
def product_detail(request, pk: int):
    if HAS_MODEL:
        try:
            p = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404('Product not found')
        return JsonResponse(product_to_dict(p))
    else:
        products = _load_products_from_file()
        for prod in products:
            if int(prod.get('id', -1)) == int(pk):
                return JsonResponse(product_to_dict(prod))
        raise Http404('Product not found')

def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a or "", b or "").ratio()

@require_GET
def product_similar(request, pk: int):
    """Retourne les 5 produits les plus proches par similarité nom+description."""
    if HAS_MODEL:
        try:
            base = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404('Product not found')

        base_text = (base.name or "") + " \n " + (base.description or "")
        candidates = Product.objects.exclude(pk=pk)
        scored = []
        for c in candidates:
            text = (c.name or "") + " \n " + (c.description or "")
            score = _similarity(base_text, text)
            scored.append((score, c))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = [product_to_dict(p) for score, p in scored[:5]]
        return JsonResponse({'product': product_to_dict(base), 'similar': top})
    else:
        products = _load_products_from_file()
        base = None
        for prod in products:
            if int(prod.get('id', -1)) == int(pk):
                base = prod
                break
        if base is None:
            raise Http404('Product not found')

        base_text = (base.get('name') or "") + " \n " + (base.get('description') or "")
        scored = []
        for prod in products:
            if int(prod.get('id', -1)) == int(pk):
                continue
            text = (prod.get('name') or "") + " \n " + (prod.get('description') or "")
            score = _similarity(base_text, text)
            scored.append((score, prod))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = [product_to_dict(p) for score, p in scored[:5]]
        return JsonResponse({'product': product_to_dict(base), 'similar': top})

# --- Nouveaux endpoints protégés (vendeurs uniquement) ---


def user_is_vendor(user) -> bool:
    return user.is_authenticated and user.groups.filter(name=VENDOR_GROUP_NAME).exists()

@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def product_create(request):
    if not HAS_MODEL:
        return Response({'detail': 'Model Product indisponible (fallback JSON). Création désactivée.'}, status=503)

    if not user_is_vendor(request.user):
        return Response({'detail': "Seuls les vendeurs peuvent créer des produits."}, status=status.HTTP_403_FORBIDDEN)

    data = request.data  # DRF gère JSON et multipart automatiquement

    name = (data.get('name') or '').strip()
    if not name:
        return Response({'detail': 'name est requis'}, status=400)

    try:
        price = data.get('price')
        price = float(price) if price is not None else None
    except Exception:
        return Response({'detail': 'price invalide'}, status=400)

    stock = int(data.get('stock') or 0)
    family = (data.get('family') or '').strip()
    concentration = (data.get('concentration') or '').strip()
    image_url = (data.get('image_url') or '').strip()
    tags = data.get('tags')
    if isinstance(tags, str):
        try:
            tags = json.loads(tags)
        except Exception:
            tags = [t.strip() for t in tags.split(',') if t.strip()]
    tags = tags or []

    p = Product(
        owner=request.user,
        name=name,
        description=data.get('description') or '',
        price=price,
        stock=stock,
        family=family,
        concentration=concentration,
        image_url=image_url,
        tags=tags
    )

    if 'image' in request.FILES:
        p.image = request.FILES['image']

    p.save()
    return Response(product_to_dict(p), status=status.HTTP_201_CREATED)


@api_view(["PUT", "PATCH"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def product_update(request, pk: int):
    if not HAS_MODEL:
        return Response({'detail': 'Model Product indisponible (fallback JSON). Edition désactivée.'}, status=503)
    try:
        p = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        raise Http404('Product not found')

    if not user_is_vendor(request.user) or p.owner_id != request.user.id:
        return Response({'detail': "Vous ne pouvez modifier que vos propres produits."}, status=status.HTTP_403_FORBIDDEN)

    data = request.data

    for field in ['name', 'description', 'family', 'concentration', 'image_url']:
        if field in data:
            setattr(p, field, (data.get(field) or '').strip())

    if 'price' in data:
        try:
            p.price = float(data.get('price'))
        except Exception:
            return Response({'detail': 'price invalide'}, status=400)

    if 'stock' in data:
        try:
            p.stock = int(data.get('stock'))
        except Exception:
            return Response({'detail': 'stock invalide'}, status=400)

    if 'tags' in data:
        tags = data.get('tags')
        if isinstance(tags, str):
            try:
                tags = json.loads(tags)
            except Exception:
                tags = [t.strip() for t in tags.split(',') if t.strip()]
        p.tags = tags or []

    if 'image' in request.FILES:
        p.image = request.FILES['image']

    p.save()
    return Response(product_to_dict(p), status=200)


@api_view(["DELETE"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def product_delete(request, pk: int):
    if not HAS_MODEL:
        return Response({'detail': 'Model Product indisponible (fallback JSON). Suppression désactivée.'}, status=503)
    try:
        p = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        raise Http404('Product not found')

    if not user_is_vendor(request.user) or p.owner_id != request.user.id:
        return Response({'detail': "Vous ne pouvez supprimer que vos propres produits."}, status=status.HTTP_403_FORBIDDEN)

    p.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

# backend/products/views.py
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.views.decorators.csrf import csrf_exempt

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def product_upload_image(request, pk: int):
    """
    Upload d'image pour un produit du vendeur courant.
    Accept: multipart/form-data avec champ 'image'.
    """
    if not HAS_MODEL:
        return JsonResponse({'detail': 'Model not available'}, status=400)

    try:
        p = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        raise Http404('Product not found')

    # propriétaire requis
    if getattr(p, 'owner_id', None) != request.user.id and not request.user.is_superuser:
        return JsonResponse({'detail': 'Not your product'}, status=403)

    img = request.FILES.get('image')
    if not img:
        return JsonResponse({'detail': 'No image file'}, status=400)

    # sauvegarder dans ImageField
    p.image.save(img.name, img, save=True)
    # on peut effacer l'ancienne URL legacy si on veut
    if hasattr(p, 'image_url'):
        p.image_url = ''
    p.save()

    return JsonResponse(product_to_dict(p))

# backend/products/views.py (à ajouter)
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def product_upload_image(request, pk):
    """
    Upload d'une image depuis un <input type="file">.
    Champ attendu: 'image' (multipart/form-data).
    Permissions: owner du produit ou staff.
    """
    from .models import Product
    prod = get_object_or_404(Product, pk=pk)
    user = request.user
    if not (getattr(prod, 'owner_id', None) == user.id or user.is_staff):
        return JsonResponse({'detail': 'Forbidden'}, status=403)

    file = request.FILES.get('image')
    if not file:
        return JsonResponse({'detail': 'No image'}, status=400)

    # sauver dans ImageField
    prod.image.save(file.name, file, save=True)
    # renvoyer le produit (même format que product_to_dict)
    from .views import product_to_dict  # si dans ce fichier, pas besoin de cette import
    return JsonResponse(product_to_dict(prod))
