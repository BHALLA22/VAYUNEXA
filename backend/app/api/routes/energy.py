"""
FILE: backend/app/api/routes/energy.py

PURPOSE:
GET /api/v1/energy/current
GET /api/v1/energy/today
GET /api/v1/energy/history
GET /api/v1/energy/comparison
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.services import energy_service


router = APIRouter(
    prefix="/energy",
    tags=["energy"],
)


@router.get("/current")
def current_power(
    device_id: str = Query(...),
    db: Session = Depends(get_db),
):
    return energy_service.get_current_power(
        db,
        device_id,
    )


@router.get("/today")
def energy_today(
    device_id: str = Query(...),
    db: Session = Depends(get_db),
):
    return energy_service.get_energy_today(
        db,
        device_id,
    )


@router.get("/history")
def energy_history(
    device_id: str = Query(...),
    days: int = Query(
        7,
        ge=1,
        le=90,
    ),
    db: Session = Depends(get_db),
):
    return energy_service.get_energy_history(
        db,
        device_id,
        days,
    )


@router.get("/comparison")
def fixed_vs_adaptive(
    device_id: str = Query(...),
    days: int = Query(
        7,
        ge=1,
        le=90,
    ),
    db: Session = Depends(get_db),
):
    return energy_service.get_fixed_vs_adaptive_comparison(
        db,
        device_id,
        days,
    )
