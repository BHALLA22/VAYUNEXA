"""
FILE: backend/app/schemas/weather.py

PURPOSE:
Pydantic schemas for weather current/forecast responses.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class WeatherOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    record_type: str
    fetched_at: datetime
    valid_at: datetime
    latitude: float
    longitude: float
    wind_speed: float | None
    wind_direction: float | None
    temperature: float | None
    humidity: float | None
    pressure: float | None
    precipitation: float | None
    cloud_cover: float | None
    source: str
