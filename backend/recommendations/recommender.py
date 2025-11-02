import threading
from typing import List, Dict, Any
import os
import json
import joblib
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# Simple in-memory recommender with thread-safe train/predict
_lock = threading.Lock()
_model = {
    'vectorizer': None,
    'tfidf_matrix': None,
    'product_index': {},  # product_id -> row index
    'index_product': {},  # row index -> product dict
}

# path to persist trained model
_MODEL_FILE = os.path.join(os.path.dirname(__file__), 'model.joblib')


def _save_model():
    try:
        to_save = {
            'vectorizer': _model['vectorizer'],
            'tfidf_matrix': _model['tfidf_matrix'],
            'product_index': _model['product_index'],
            'index_product': _model['index_product'],
        }
        joblib.dump(to_save, _MODEL_FILE)
    except Exception:
        # don't fail training on persistence problems
        pass


def _load_model_if_exists():
    if os.path.exists(_MODEL_FILE):
        try:
            loaded = joblib.load(_MODEL_FILE)
            with _lock:
                _model.update(loaded)
        except Exception:
            pass


# attempt to load persisted model at import time
_load_model_if_exists()


def _load_products_from_db_or_file(get_products_func=None):
    """Return list of product dicts with keys id,name,description,tags."""
    if get_products_func:
        products = get_products_func()
        if products:
            return products

    # try reading from Product model if available
    try:
        from products.models import Product
        qs = Product.objects.all()
        if qs.exists():
            out = []
            for p in qs:
                out.append({
                    'id': p.id,
                    'name': p.name,
                    'description': p.description,
                    'tags': p.tags if getattr(p, 'tags', None) is not None else [],
                })
            return out
    except Exception:
        # fall back to JSON file
        pass

    data_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'products', 'data', 'products.json')
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def train(get_products_func=None):
    """Train TF-IDF on products. get_products_func should return iterable of product dicts."""
    products = _load_products_from_db_or_file(get_products_func=get_products_func)
    docs = []
    index = {}
    idx = 0
    for p in products:
        text = (p.get('name') or '') + ' ' + (p.get('description') or '') + ' ' + ' '.join(p.get('tags', []))
        docs.append(text)
        pid = int(p.get('id'))
        index[pid] = idx
        idx += 1

    if not docs:
        return {'n_products': 0}

    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    tfidf = vectorizer.fit_transform(docs)

    with _lock:
        _model['vectorizer'] = vectorizer
        _model['tfidf_matrix'] = tfidf
        _model['product_index'] = index
        _model['index_product'] = {v: p for p, v in zip(products, range(len(products)))}

    # persist model to disk for faster restarts
    _save_model()

    return {'n_products': len(docs)}


def similar_products(product_id: int, k: int = 5) -> List[Dict[str, Any]]:
    """Return up to k similar products as list of product dicts (may be empty)."""
    with _lock:
        if _model['tfidf_matrix'] is None:
            return []
        index = _model['product_index'].get(int(product_id))
        if index is None:
            return []
        tfidf = _model['tfidf_matrix']

    # compute cosine similarities
    cosine_similarities = linear_kernel(tfidf[index:index+1], tfidf).flatten()
    # get indices sorted by score (highest first)
    related_idx = cosine_similarities.argsort()[::-1]
    # skip the item itself
    related_idx = [i for i in related_idx if i != index]
    topk = related_idx[:k]

    results = []
    for i in topk:
        prod = _model['index_product'].get(i)
        if prod:
            results.append(prod)
    return results
