"""
FILE: backend/app/core/security.py

PURPOSE:
Simple API-key validation for write operations.

This is prototype-level security and is not intended to replace
production authentication, per-device credentials, key rotation,
or rate limiting.
"""

from fastapi import Header, HTTPException, status

from app.core.config import settings


def verify_api_token(
    x_api_key: str | None = Header(default=None),
) -> None:
    """
    FastAPI dependency for protected write endpoints.

    Required header:

        X-API-Key: <token>
    """

    if not x_api_key or x_api_key != settings.api_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid X-API-Key header.",
        )
