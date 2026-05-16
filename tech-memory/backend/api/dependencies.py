"""FastAPI dependency injection."""

from db.session import get_db

__all__ = ["get_db"]
