#!/usr/bin/env python3
"""WSGI entrypoint for Vercel deployment.

Satisfies Vercel Python Serverless runtime autodetection while serving
the Field Notes Tender Command Center dashboard and REST APIs.
"""
import json
import sqlite3
import mimetypes
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HTML_PATH = ROOT / "intel" / "monitoring_preview.html"
DB_PATH = ROOT / "intel" / "data" / "intel.db"

def get_bids_json():
    if not DB_PATH.exists():
        return json.dumps([])
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT bid_number, title, org_name, ministry, dept, state,
                   status, end_date, start_date, capacity_class, quantity,
                   est_value, source_url
            FROM bids
            WHERE relevant = 1
            ORDER BY end_date ASC
        """).fetchall()
        return json.dumps([dict(r) for r in rows])
    except Exception as e:
        return json.dumps({"error": str(e)})

def app(environ, start_response):
    """Standard WSGI entrypoint for Vercel."""
    path = environ.get("PATH_INFO", "/")

    # API endpoint
    if path == "/api/bids":
        data = get_bids_json().encode("utf-8")
        start_response("200 OK", [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(data))),
            ("Access-Control-Allow-Origin", "*"),
        ])
        return [data]

    # Serve Command Center HTML
    if path in ("/", "/index.html", "/preview"):
        if HTML_PATH.exists():
            content = HTML_PATH.read_bytes()
            start_response("200 OK", [
                ("Content-Type", "text/html; charset=utf-8"),
                ("Content-Length", str(len(content))),
                ("Cache-Control", "public, max-age=60"),
            ])
            return [content]

    # Try static file lookup
    file_path = ROOT / path.lstrip("/")
    if file_path.exists() and file_path.is_file():
        mime_type, _ = mimetypes.guess_type(str(file_path))
        mime_type = mime_type or "application/octet-stream"
        content = file_path.read_bytes()
        start_response("200 OK", [
            ("Content-Type", mime_type),
            ("Content-Length", str(len(content))),
        ])
        return [content]

    # Fallback to main dashboard
    if HTML_PATH.exists():
        content = HTML_PATH.read_bytes()
        start_response("200 OK", [
            ("Content-Type", "text/html; charset=utf-8"),
            ("Content-Length", str(len(content))),
        ])
        return [content]

    start_response("404 Not Found", [("Content-Type", "text/plain")])
    return [b"Not Found"]

# Aliases for Vercel WSGI / Serverless
application = app
handler = app

# For local testing: python3 app.py
if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    port = 8787
    print(f"Starting local server at http://127.0.0.1:{port}")
    server = make_server("127.0.0.1", port, app)
    server.serve_forever()
