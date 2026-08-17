"""
FILE: backend/app/api/routes/health.py

PURPOSE:
Health/liveness endpoint and temporary configuration diagnostics.
"""

from datetime import datetime, timezone

from fastapi import APIRouter

from app.core.config import settings


router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "vayunexa-backend",
        "time": datetime.now(timezone.utc),
    }


@router.get("/health/config")
def config_check():
    token = settings.api_token

    return {
        "status": "ok",
        "api_token_configured": bool(token),
        "api_token_length": len(token),
        "api_token_is_default": token == "dev-token-change-me",
        "environment": settings.environment,
    }