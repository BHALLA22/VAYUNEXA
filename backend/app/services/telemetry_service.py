"""
FILE: backend/app/services/telemetry_service.py

PURPOSE:
Business logic for ingesting and reading telemetry.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.telemetry import Telemetry
from app.models.turbine import Turbine
from app.schemas.telemetry import TelemetryIn


def get_or_create_turbine(
    db: Session,
    device_id: str,
) -> Turbine:
    turbine = db.execute(
        select(Turbine).where(
            Turbine.device_id == device_id
        )
    ).scalar_one_or_none()

    if turbine is None:
        turbine = Turbine(
            device_id=device_id,
            name=f"Turbine {device_id}",
            status="online",
        )
        db.add(turbine)
        db.commit()
        db.refresh(turbine)

    return turbine


def _ensure_aware_utc(value: datetime) -> datetime:
    """
    Normalize timestamps to timezone-aware UTC.

    SQLite may return datetime values without tzinfo,
    while PostgreSQL may preserve timezone information.
    """
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value


def _estimate_servo_energy_wh(
    previous: Telemetry | None,
    new_angles: tuple[float, float, float],
    interval_seconds: float,
) -> float:
    """
    Rough prototype estimate of servo energy use.

    This is an estimate, not a measured hardware value.
    """

    if previous is None:
        return 0.0

    prev_angles = (
        previous.flap_angle_1,
        previous.flap_angle_2,
        previous.flap_angle_3,
    )

    total_degrees_moved = sum(
        abs(a - b)
        for a, b in zip(
            new_angles,
            prev_angles,
        )
    )

    if total_degrees_moved <= 0:
        return 0.0

    power_mw = (
        total_degrees_moved
        * settings.servo_energy_mw_per_degree
    )

    hours = interval_seconds / 3600.0

    return (
        power_mw / 1000.0
    ) * hours


def ingest_telemetry(
    db: Session,
    payload: TelemetryIn,
) -> Telemetry:

    turbine = get_or_create_turbine(
        db,
        payload.device_id,
    )

    turbine.status = (
        "online"
        if payload.mode != "simulation"
        else "simulation"
    )

    turbine.mode = payload.mode

    # Power is always calculated server-side.
    power_watts = round(
        payload.voltage * payload.current,
        4,
    )

    previous = db.execute(
        select(Telemetry)
        .where(
            Telemetry.device_id == payload.device_id
        )
        .order_by(
            desc(Telemetry.timestamp)
        )
        .limit(1)
    ).scalar_one_or_none()

    interval_seconds = 30.0

    ts = _ensure_aware_utc(
        payload.resolved_timestamp()
    )

    if previous is not None:
        delta = (
            ts
            - _ensure_aware_utc(
                previous.timestamp
            )
        ).total_seconds()

        if delta > 0:
            interval_seconds = min(
                delta,
                3600,
            )

    servo_energy_wh = _estimate_servo_energy_wh(
        previous,
        (
            payload.flap_angle_1,
            payload.flap_angle_2,
            payload.flap_angle_3,
        ),
        interval_seconds,
    )

    record = Telemetry(
        turbine_id=turbine.id,
        device_id=payload.device_id,
        timestamp=ts,
        wind_speed=payload.wind_speed,
        wind_direction=payload.wind_direction,
        rpm=payload.rpm,
        voltage=payload.voltage,
        current=payload.current,
        power=power_watts,
        flap_angle_1=payload.flap_angle_1,
        flap_angle_2=payload.flap_angle_2,
        flap_angle_3=payload.flap_angle_3,
        temperature=payload.temperature,
        humidity=payload.humidity,
        mode=payload.mode,
        servo_energy_wh=servo_energy_wh,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def get_latest_telemetry(
    db: Session,
    device_id: str,
) -> Telemetry | None:

    return db.execute(
        select(Telemetry)
        .where(
            Telemetry.device_id == device_id
        )
        .order_by(
            desc(Telemetry.timestamp)
        )
        .limit(1)
    ).scalar_one_or_none()


def get_telemetry_history(
    db: Session,
    device_id: str,
    hours: int,
) -> list[Telemetry]:

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
            Telemetry.timestamp.asc()
        )
    ).scalars().all()

    return list(rows)
