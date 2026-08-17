"""
FILE: backend/app/api/dependencies.py

PURPOSE:
Shared FastAPI dependencies re-exported for convenience so
route files only need one import line.
"""

from app.core.security import verify_api_token
from app.db.database import get_db

__all__ = [
    "get_db",
    "verify_api_token",
]
