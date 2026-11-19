# Vercel entrypoint: the Python runtime serves this ASGI app.
import sys
from pathlib import Path

# Make the project root importable so "app" resolves from api/.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app  # noqa: E402,F401
