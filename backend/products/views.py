from django.http import JsonResponse, Http404
from django.views.decorators.http import require_GET
from difflib import SequenceMatcher
import json
import os

# Try to import Product model; if missing, we'll fall back to a JSON data file
try:
	from .models import Product  # type: ignore
	HAS_MODEL = True
except Exception:
	Product = None
	HAS_MODEL = False

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'products.json')

def _load_products_from_file():
	try:
		with open(DATA_FILE, 'r', encoding='utf-8') as f:
			data = json.load(f)
			return data
	except Exception:
		return []


def product_to_dict(p) -> dict:
	# p can be a model instance or a dict loaded from JSON
	if HAS_MODEL and hasattr(p, 'id'):
		return {
			'id': p.id,
			'name': p.name,
			'description': p.description,
			'price': float(p.price) if getattr(p, 'price', None) is not None else None,
			'stock': getattr(p, 'stock', None),
			'family': getattr(p, 'family', None),
			'concentration': getattr(p, 'concentration', None),
			# Prefer uploaded image file URL if present, otherwise legacy image_url
			'image_url': (getattr(p, 'image', None).url if getattr(p, 'image', None) and getattr(p, 'image', None).name else getattr(p, 'image_url', None)),
			'tags': getattr(p, 'tags', []) or [],
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
		}


@require_GET
def products_list(request):
	# If the client didn't provide any parameters, keep legacy behaviour and
	# return a plain list to avoid breaking the static frontend which expects
	# an array of products.
	has_params = any(k in request.GET for k in ('q', 'page', 'page_size'))
	if not has_params:
		if HAS_MODEL:
			qs = Product.objects.all()
			data = [product_to_dict(p) for p in qs]
		else:
			data = _load_products_from_file()
		return JsonResponse(data, safe=False)

	# server-side simple search and pagination (activated when params provided)
	q = request.GET.get('q', '').strip()
	try:
		page = max(1, int(request.GET.get('page', '1')))
	except Exception:
		page = 1
	try:
		page_size = max(1, min(100, int(request.GET.get('page_size', '20'))))
	except Exception:
		page_size = 20

	if HAS_MODEL:
		qs = Product.objects.all()
		if q:
			# search in name, description and tags (tags is JSONField)
			from django.db import models as dj_models
			qs = qs.filter(
				dj_models.Q(name__icontains=q) | dj_models.Q(description__icontains=q) | dj_models.Q(tags__icontains=q)
			)
		total = qs.count()
		start = (page - 1) * page_size
		end = start + page_size
		data = [product_to_dict(p) for p in qs.order_by('id')[start:end]]
	else:
		data = _load_products_from_file()
		if q:
			qlow = q.lower()
			data = [p for p in data if qlow in (p.get('name') or '').lower() or qlow in (p.get('description') or '').lower() or qlow in ' '.join(p.get('tags', [])).lower()]
		total = len(data)
		start = (page - 1) * page_size
		end = start + page_size
		data = data[start:end]

	return JsonResponse({'results': data, 'count': total, 'page': page, 'page_size': page_size}, safe=False)


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
	"""Return top 5 similar products based on name+description similarity.

	This is a simple, dependency-free fallback recommender using
	difflib.SequenceMatcher. It is synchronous and intended for dev/testing.
	"""
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

