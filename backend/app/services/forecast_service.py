"""
FILE: backend/app/services/forecast_service.py

PURPOSE:
Produces hourly energy forecasts.

The service first attempts to load the trained XGBoost model from
ai/models/. If the trained model is unavailable, it uses a clearly
labeled heuristic fallback so the dashboard can still operate in
demo mode.
"""

import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.telemetry import Telemetry
from app.models.weather import Weather


_model_cache = {
    "model": None,
    "feature_names": None,
    "loaded": False,
}


def _resolve_path(relative: str) -> Path:
    """
    Resolve paths relative to the backend directory.
    """

    backend_dir = Path(__file__).resolve().parent.parent.parent

    return (backend_dir / relative).resolve()


def _try_load_model():
    """
    Load the trained model once and cache it for the process.
    """

    if _model_cache["loaded"]:
        return (
            _model_cache["model"],
            _model_cache["feature_names"],
        )

    _model_cache["loaded"] = True

    model_path = _resolve_path(
        settings.ai_model_path
    )

    features_path = model_path.with_name(
        model_path.stem + "_features.json"
    )

    if not model_path.exists():
        return None, None

    try:
        import joblib

        model = joblib.load(model_path)

        feature_names = (
            json.loads(
                features_path.read_text(
                    encoding="utf-8"
                )
            )
            if features_path.exists()
            else None
        )

        _model_cache["model"] = model
        _model_cache["feature_names"] = feature_names

        return model, feature_names

    except Exception:
        return None, None


def _recent_avg_power(
    db: Session,
    device_id: str,
    hours: int = 6,
) -> float:

    since = (
        datetime.now(timezone.utc)
        - timedelta(hours=hours)
    )

    rows = db.execute(
        select(Telemetry)
        .where(
            Telemetry.device_id == device_id,
            Telemetry.timestamp >= since,
        )
        .order_by(
            Telemetry.timestamp.desc()
        )
        .limit(200)
    ).scalars().all()

    if not rows:
        return 0.0

    return sum(
        row.power for row in rows
    ) / len(rows)


def _heuristic_forecast(
    db: Session,
    device_id: str,
    horizon_hours: int,
) -> list[dict]:
    """
    Transparent fallback used before a trained AI model exists.

    This is a prototype heuristic, NOT an AI prediction.
    """

    base_power = max(
        _recent_avg_power(
            db,
            device_id,
        ),
        5.0,
    )

    now = datetime.now(timezone.utc)

    points = []

    for hour_offset in range(
        1,
        horizon_hours + 1,
    ):
        target_time = (
            now
            + timedelta(hours=hour_offset)
        )

        # Mild diurnal variation used only for demo purposes.
        diurnal_factor = (
            1.0
            + 0.15
            * math.sin(
                (target_time.hour - 6)
                / 24
                * 2
                * math.pi
            )
        )

        predicted_wh = round(
            base_power
            * diurnal_factor,
            3,
        )

        points.append(
            {
                "forecast_for": target_time,
                "predicted_energy_wh": predicted_wh,
            }
        )

    return points


def _model_based_forecast(
    db: Session,
    device_id: str,
    horizon_hours: int,
    model,
    feature_names,
) -> list[dict] | None:
    """
    Build future feature rows and predict using the trained model.

    Uses the most recent telemetry and cached weather forecast.
    Returns None when insufficient data is available.
    """

    import pandas as pd

    latest = db.execute(
        select(Telemetry)
        .where(
            Telemetry.device_id == device_id
        )
        .order_by(
            Telemetry.timestamp.desc()
        )
        .limit(1)
    ).scalar_one_or_none()

    if latest is None:
        return None

    weather_rows = db.execute(
        select(Weather)
        .where(
            Weather.record_type == "forecast"
        )
        .order_by(
            Weather.valid_at.asc()
        )
    ).scalars().all()

    now = datetime.now(timezone.utc)

    points = []

    for hour_offset in range(
        1,
        horizon_hours + 1,
    ):
        target_time = (
            now
            + timedelta(hours=hour_offset)
        )

        if weather_rows:
            weather = min(
                weather_rows,
                key=lambda item: abs(
                    (
                        item.valid_at
                        - target_time
                    ).total_seconds()
                ),
            )
        else:
            weather = None

        wind_speed = (
            weather.wind_speed
            if weather
            and weather.wind_speed is not None
            else latest.wind_speed
        )

        temperature = (
            weather.temperature
            if weather
            and weather.temperature is not None
            else (
                latest.temperature
                if latest.temperature is not None
                else 25.0
            )
        )

        humidity = (
            weather.humidity
            if weather
            and weather.humidity is not None
            else (
                latest.humidity
                if latest.humidity is not None
                else 50.0
            )
        )

        pressure = (
            weather.pressure
            if weather
            and weather.pressure is not None
            else 1013.0
        )

        precipitation = (
            weather.precipitation
            if weather
            and weather.precipitation is not None
            else 0.0
        )

        cloud_cover = (
            weather.cloud_cover
            if weather
            and weather.cloud_cover is not None
            else 50.0
        )

        row = {
            "wind_speed": wind_speed,
            "rpm": latest.rpm,
            "voltage": latest.voltage,
            "current": latest.current,
            "flap_angle_1": latest.flap_angle_1,
            "flap_angle_2": latest.flap_angle_2,
            "flap_angle_3": latest.flap_angle_3,
            "temperature": temperature,
            "humidity": humidity,
            "pressure": pressure,
            "precipitation": precipitation,
            "cloud_cover": cloud_cover,
            "hour": target_time.hour,
            "day_of_week": target_time.weekday(),
            "hour_sin": math.sin(
                2
                * math.pi
                * target_time.hour
                / 24
            ),
            "hour_cos": math.cos(
                2
                * math.pi
                * target_time.hour
                / 24
            ),
        }

        points.append(
            (
                target_time,
                row,
            )
        )

    frame = pd.DataFrame(
        [item[1] for item in points]
    )

    if feature_names:
        frame = frame[feature_names]

    predictions = model.predict(frame)

    return [
        {
            "forecast_for": target_time,
            "predicted_energy_wh": max(
                round(
                    float(prediction),
                    3,
                ),
                0.0,
            ),
        }
        for (target_time, _), prediction
        in zip(points, predictions)
    ]


def generate_forecast(
    db: Session,
    device_id: str,
    horizon_hours: int,
) -> dict:

    model, feature_names = _try_load_model()

    model_version = "heuristic-fallback"
    is_ai_model = False
    points = None

    if model is not None:
        try:
            points = _model_based_forecast(
                db,
                device_id,
                horizon_hours,
                model,
                feature_names,
            )

            if points is not None:
                model_version = "xgboost-v1"
                is_ai_model = True

        except Exception:
            # Fall back safely to the heuristic.
            points = None

    if points is None:
        points = _heuristic_forecast(
            db,
            device_id,
            horizon_hours,
        )

    total = sum(
        point["predicted_energy_wh"]
        for point in points
    )

    return {
        "device_id": device_id,
        "horizon_hours": horizon_hours,
        "generated_at": datetime.now(timezone.utc),
        "model_version": model_version,
        "is_ai_model": is_ai_model,
        "total_predicted_energy_wh": round(
            total,
            3,
        ),
        "points": points,
    }
