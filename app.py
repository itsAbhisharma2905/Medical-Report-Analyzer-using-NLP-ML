"""FastAPI entrypoint recognized by local Uvicorn and Vercel."""

from api.server import app

__all__ = ["app"]
