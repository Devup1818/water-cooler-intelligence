"""Vercel entrypoint alias."""
from app import app as _app, application as _application, handler as _handler

app = _app
application = _application
handler = _handler
