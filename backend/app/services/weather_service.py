"""
FILE: backend/app/services/weather_service.py

PURPOSE:
Fetches weather from a pluggable provider and normalizes it into
the internal Weather model shape.

Default provider: Open-Meteo (no API key required).
OpenWeatherMap can be selected through configuration.
"""

from datetime import datetime, timezone

import requests
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.weather import Weather


class WeatherProviderError(Exception):
    pass


def _fetch_open_meteo() -> dict:
    """
    Fetch weather from Open-Meteo.

    No API key is required.
    """

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": settings.weather_lat,
        "longitude": settings.weather_lon,
        "current": (
            "temperature_2m,relative_humidity_2m,"
            "wind_speed_10m,wind_direction_10m,"
            "surface_pressure,precipitation,cloud_cover"
        ),
        "hourly": (
            "temperature_2m,relative_humidity_2m,"
            "wind_speed_10m,wind_direction_10m,"
            "surface_pressure,precipitation,cloud_cover"
        ),
        "forecast_days": 5,
        "timezone": "UTC",
    }

    response = requests.get(
        url,
        params=params,
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    current = {
        "record_type": "current",
        "valid_at": data["current"]["time"],
        "wind_speed": data["current"].get("wind_speed_10m"),
        "wind_direction": data["current"].get(
            "wind_direction_10m"
        ),
        "temperature": data["current"].get(
            "temperature_2m"
        ),
        "humidity": data["current"].get(
            "relative_humidity_2m"
        ),
        "pressure": data["current"].get(
            "surface_pressure"
        ),
        "precipitation": data["current"].get(
            "precipitation"
        ),
        "cloud_cover": data["current"].get(
            "cloud_cover"
        ),
    }

    forecast_points = []

    hourly = data.get("hourly", {})
    times = hourly.get("time", [])

    wind_speeds = hourly.get(
        "wind_speed_10m",
        [None] * len(times),
    )

    wind_directions = hourly.get(
        "wind_direction_10m",
        [None] * len(times),
    )

    temperatures = hourly.get(
        "temperature_2m",
        [None] * len(times),
    )

    humidities = hourly.get(
        "relative_humidity_2m",
        [None] * len(times),
    )

    pressures = hourly.get(
        "surface_pressure",
        [None] * len(times),
    )

    precipitations = hourly.get(
        "precipitation",
        [None] * len(times),
    )

    cloud_covers = hourly.get(
        "cloud_cover",
        [None] * len(times),
    )

    for index, timestamp in enumerate(times):
        forecast_points.append(
            {
                "record_type": "forecast",
                "valid_at": timestamp,
                "wind_speed": wind_speeds[index],
                "wind_direction": wind_directions[index],
                "temperature": temperatures[index],
                "humidity": humidities[index],
                "pressure": pressures[index],
                "precipitation": precipitations[index],
                "cloud_cover": cloud_covers[index],
            }
        )

    return {
        "current": current,
        "forecast": forecast_points,
        "source": "open-meteo",
    }


def _fetch_openweathermap() -> dict:
    """
    Fetch weather from OpenWeatherMap One Call API.

    Requires WEATHER_API_KEY.
    """

    if not settings.weather_api_key:
        raise WeatherProviderError(
            "WEATHER_API_KEY is not set but "
            "provider=openweathermap"
        )

    url = "https://api.openweathermap.org/data/3.0/onecall"

    params = {
        "lat": settings.weather_lat,
        "lon": settings.weather_lon,
        "appid": settings.weather_api_key,
        "units": "metric",
        "exclude": "minutely,alerts",
    }

    response = requests.get(
        url,
        params=params,
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    current_data = data["current"]

    current = {
        "record_type": "current",
        "valid_at": datetime.fromtimestamp(
            current_data["dt"],
            tz=timezone.utc,
        ).isoformat(),
        "wind_speed": current_data.get("wind_speed"),
        "wind_direction": current_data.get("wind_deg"),
        "temperature": current_data.get("temp"),
        "humidity": current_data.get("humidity"),
        "pressure": current_data.get("pressure"),
        "precipitation": (
            current_data.get("rain", {}).get("1h", 0)
            if current_data.get("rain")
            else 0
        ),
        "cloud_cover": current_data.get("clouds"),
    }

    forecast_points = []

    for hourly_data in data.get("hourly", []):
        forecast_points.append(
            {
                "record_type": "forecast",
                "valid_at": datetime.fromtimestamp(
                    hourly_data["dt"],
                    tz=timezone.utc,
                ).isoformat(),
                "wind_speed": hourly_data.get("wind_speed"),
                "wind_direction": hourly_data.get("wind_deg"),
                "temperature": hourly_data.get("temp"),
                "humidity": hourly_data.get("humidity"),
                "pressure": hourly_data.get("pressure"),
                "precipitation": (
                    hourly_data.get("rain", {}).get(
                        "1h",
                        0,
                    )
                    if hourly_data.get("rain")
                    else 0
                ),
                "cloud_cover": hourly_data.get("clouds"),
            }
        )

    return {
        "current": current,
        "forecast": forecast_points,
        "source": "openweathermap",
    }


def fetch_and_store_weather(
    db: Session,
) -> Weather:
    """
    Fetch fresh weather, store all points in the DB,
    and return the current row.

    If the external provider fails, the most recent cached
    current weather row is returned when available.
    """

    try:
        if (
            settings.weather_api_provider
            == "openweathermap"
        ):
            data = _fetch_openweathermap()
        else:
            data = _fetch_open_meteo()

    except (
        requests.RequestException,
        WeatherProviderError,
        KeyError,
    ) as exc:

        cached = db.execute(
            select(Weather)
            .where(
                Weather.record_type == "current"
            )
            .order_by(
                Weather.fetched_at.desc()
            )
            .limit(1)
        ).scalar_one_or_none()

        if cached:
            return cached

        raise WeatherProviderError(
            "Weather fetch failed and no cached data exists: "
            f"{exc}"
        ) from exc

    def _row(point: dict) -> Weather:
        return Weather(
            record_type=point["record_type"],
            valid_at=point["valid_at"],
            latitude=settings.weather_lat,
            longitude=settings.weather_lon,
            wind_speed=point.get("wind_speed"),
            wind_direction=point.get(
                "wind_direction"
            ),
            temperature=point.get(
                "temperature"
            ),
            humidity=point.get("humidity"),
            pressure=point.get("pressure"),
            precipitation=point.get(
                "precipitation"
            ),
            cloud_cover=point.get(
                "cloud_cover"
            ),
            source=data["source"],
        )

    current_row = _row(data["current"])

    db.add(current_row)

    for point in data["forecast"]:
        db.add(_row(point))

    db.commit()
    db.refresh(current_row)

    return current_row


def get_cached_current(
    db: Session,
) -> Weather | None:
    return db.execute(
        select(Weather)
        .where(
            Weather.record_type == "current"
        )
        .order_by(
            Weather.fetched_at.desc()
        )
        .limit(1)
    ).scalar_one_or_none()


def get_cached_forecast(
    db: Session,
    hours: int = 96,
) -> list[Weather]:
    rows = db.execute(
        select(Weather)
        .where(
            Weather.record_type == "forecast"
        )
        .order_by(
            Weather.valid_at.asc()
        )
        .limit(hours)
    ).scalars().all()

    return list(rows)
