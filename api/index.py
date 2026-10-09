from http.server import BaseHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / "index.html"
if not HTML_PATH.exists():
    HTML_PATH = ROOT / "intel" / "monitoring_preview.html"

HTML_BYTES = HTML_PATH.read_bytes() if HTML_PATH.exists() else b"<h1>Water Cooler Tender Command Center</h1>"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(HTML_BYTES)))
        self.send_header("Cache-Control", "public, max-age=60")
        self.end_headers()
        self.wfile.write(HTML_BYTES)
        return

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(HTML_BYTES)))
        self.end_headers()
        return

# Also support WSGI / ASGI for modern Vercel runtimes
def app(environ, start_response):
    start_response("200 OK", [
        ("Content-Type", "text/html; charset=utf-8"),
        ("Content-Length", str(len(HTML_BYTES))),
        ("Cache-Control", "public, max-age=60"),
    ])
    return [HTML_BYTES]

application = app
