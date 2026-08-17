"""
FILE: backend/app/api/routes/weather.py

PURPOSE:
GET /api/v1/weather/current  - latest fetched weather
GET /api/v1/weather/forecast - cached hourly forecast points
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.weather import WeatherOut
from app.services import weather_service


router = APIRouter(
    prefix="/weather",
    tags=["weather"],
)


_STALE_AFTER_SECONDS = 15 * 60


@router.get(
    "/current",
    response_model=WeatherOut,
)
def current_weather(
    db: Session = Depends(get_db),
):
    cached = weather_service.get_cached_current(db)

    is_stale = (
        cached is None
        or (
            datetime.now(timezone.utc)
            - cached.fetched_at
        ).total_seconds()
        > _STALE_AFTER_SECONDS
    )

    if is_stale:
        try:
            return weather_service.fetch_and_store_weather(db)

        except weather_service.WeatherProviderError as exc:
            if cached:
                return cached

            raise HTTPException(
                status_code=503,
                detail=(
                    "Weather provider unavailable: "
                    f"{exc}"
                ),
            )

    return cached


@router.get(
    "/forecast",
    response_model=list[WeatherOut],
)
def weather_forecast(
    hours: int = 96,
    db: Session = Depends(get_db),
):
    points = weather_service.get_cached_forecast(
        db,
        hours,
    )

    if not points:
        try:
            weather_service.fetch_and_store_weather(db)

            points = weather_service.get_cached_forecast(
                db,
                hours,
            )

        except weather_service.WeatherProviderError as exc:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Weather provider unavailable: "
                    f"{exc}"
                ),
            )

    return points
