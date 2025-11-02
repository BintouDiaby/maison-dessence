import http.server
import socketserver
import json
from urllib.parse import urlparse

PORT = 8000

SAMPLE_RESPONSE = {
    "product": {
        "id": 1,
        "name": "Nuit d'ambre",
        "description": "Ambre, vanille et notes florales.",
        "price": 79.0,
        "stock": 12,
        "family": "Oriental",
        "concentration": "Eau de Parfum",
        "image_url": "",
        "tags": ["ambre", "vanille"]
    },
    "similar": [
        {"id": 2, "name": "Ambre doux", "price": 69.0},
        {"id": 3, "name": "Vanille noire", "price": 85.0},
        {"id": 4, "name": "Fleur d'oranger", "price": 60.0}
    ]
}


class Handler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/products/1/similar/':
            self._set_headers(200)
            self.wfile.write(json.dumps(SAMPLE_RESPONSE).encode('utf-8'))
        else:
            self._set_headers(404, 'text/html')
            self.wfile.write(b'Page not found')

    def log_message(self, format, *args):
        # Affiche moins de logs pour garder la console propre
        print(format % args)


if __name__ == '__main__':
    with socketserver.TCPServer(('127.0.0.1', PORT), Handler) as httpd:
        print(f"Serving simple API at http://127.0.0.1:{PORT}/api/products/1/similar/")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\nArrêt du serveur.')
            httpd.server_close()
