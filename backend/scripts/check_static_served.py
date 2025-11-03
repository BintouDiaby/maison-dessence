import urllib.request
url = 'http://127.0.0.1:8000/static/app.js'
print('Fetching', url)
try:
    r = urllib.request.urlopen(url, timeout=5)
    data = r.read().decode('utf-8', errors='replace')
    lines = data.splitlines()
    print('Status OK, length', len(data), 'chars, lines', len(lines))
    sample = '\n'.join(lines[:200])
    print('\n--- HEAD (first 200 lines) ---\n')
    print(sample)
    print('\n--- SEARCHES ---')
    for token in ['toggleLike','toggleWishlist','renderCheckoutPage','p-like-btn','admin/import-products']:
        print(token, '->', 'FOUND' if token in data else 'MISSING')
except Exception as e:
    print('Error fetching:', e)
