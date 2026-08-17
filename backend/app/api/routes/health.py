"""
FILE: backend/app/api/routes/health.py

PURPOSE:
Simple health/liveness endpoint for VAYUNEXA.
"""

from datetime import datetime, timezone

from fastapi import APIRouter


router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "vayunexa-backend",
        "time": datetime.now(timezone.utc),
    }
