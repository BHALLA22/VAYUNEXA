"""
FILE: backend/app/models/__init__.py

PURPOSE:
Import every ORM model here so that all model classes are registered
with SQLAlchemy before relationship() resolution occurs.
"""

from app.models.turbine import Turbine
from app.models.telemetry import Telemetry
from app.models.weather import Weather
from app.models.forecast import Forecast
from app.models.model_metrics import ModelMetrics


__all__ = [
    "Turbine",
    "Telemetry",
    "Weather",
    "Forecast",
    "ModelMetrics",
]
