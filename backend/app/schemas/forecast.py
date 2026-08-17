"""
FILE: backend/app/schemas/forecast.py

PURPOSE:
Pydantic schemas for the /forecast/{horizon} endpoints.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ForecastPointOut(BaseModel):
    # Silences Pydantic's model_* protected namespace warning.
    model_config = ConfigDict(
        from_attributes=True,
        protected_namespaces=(),
    )

    forecast_for: datetime
    predicted_energy_wh: float


class ForecastResponse(BaseModel):
    model_config = ConfigDict(
        protected_namespaces=(),
    )

    device_id: str
    horizon_hours: int
    generated_at: datetime
    model_version: str
    is_ai_model: bool
    total_predicted_energy_wh: float
    points: list[ForecastPointOut]
