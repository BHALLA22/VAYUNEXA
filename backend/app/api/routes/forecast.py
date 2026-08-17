"""
FILE: backend/app/api/routes/forecast.py

PURPOSE:
GET /api/v1/forecast/24h
GET /api/v1/forecast/48h
GET /api/v1/forecast/72h
GET /api/v1/forecast/96h
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.forecast import ForecastResponse
from app.services import forecast_service


router = APIRouter(
    prefix="/forecast",
    tags=["forecast"],
)


def _forecast(
    device_id: str,
    hours: int,
    db: Session,
) -> ForecastResponse:
    return forecast_service.generate_forecast(
        db,
        device_id,
        hours,
    )


@router.get(
    "/24h",
    response_model=ForecastResponse,
)
def forecast_24h(
    device_id: str = Query(...),
    db: Session = Depends(get_db),
):
    return _forecast(
        device_id,
        24,
        db,
    )


@router.get(
    "/48h",
    response_model=ForecastResponse,
)
def forecast_48h(
    device_id: str = Query(...),
    db: Session = Depends(get_db),
):
    return _forecast(
        device_id,
        48,
        db,
    )


@router.get(
    "/72h",
    response_model=ForecastResponse,
)
def forecast_72h(
    device_id: str = Query(...),
    db: Session = Depends(get_db),
):
    return _forecast(
        device_id,
        72,
        db,
    )


@router.get(
    "/96h",
    response_model=ForecastResponse,
)
def forecast_96h(
    device_id: str = Query(...),
    db: Session = Depends(get_db),
):
    return _forecast(
        device_id,
        96,
        db,
    )
