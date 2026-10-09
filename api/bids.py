import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import app as _app, application as _application, handler as _handler

app = _app
application = _application
handler = _handler
