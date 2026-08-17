"""
FILE: backend/app/services/energy_service.py

PURPOSE:
All energy math lives here: current power, today's energy,
history, and the Fixed-vs-Adaptive comparison including Net
Energy Gain.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.telemetry import Telemetry


def _ensure_aware_utc(value: datetime) -> datetime:
    """Normalize SQLite/PostgreSQL timestamps to timezone-aware UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _trapezoidal_energy_wh(
    rows: list[Telemetry],
) -> float:
    """Numerically integrates power using the trapezoidal rule."""

    if len(rows) < 2:
        return 0.0

    energy_wh = 0.0

    for a, b in zip(rows, rows[1:]):
        dt_hours = (
            _ensure_aware_utc(b.timestamp)
            - _ensure_aware_utc(a.timestamp)
        ).total_seconds() / 3600.0

        if dt_hours <= 0 or dt_hours > 1:
            continue

        avg_power = (a.power + b.power) / 2.0
        energy_wh += avg_power * dt_hours

    return energy_wh


def get_current_power(
    db: Session,
    device_id: str,
) -> dict:
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
        return {
            "device_id": device_id,
            "power_watts": 0.0,
            "timestamp": None,
        }

    return {
        "device_id": device_id,
        "power_watts": latest.power,
        "timestamp": latest.timestamp,
    }


def _rows_since(
    db: Session,
    device_id: str,
    since: datetime,
) -> list[Telemetry]:
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


def get_energy_today(
    db: Session,
    device_id: str,
) -> dict:
    now = datetime.now(timezone.utc)

    start_of_day = now.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    rows = _rows_since(
        db,
        device_id,
        start_of_day,
    )

    gross_energy_wh = _trapezoidal_energy_wh(rows)
    servo_energy_wh = sum(
        r.servo_energy_wh
        for r in rows
    )

    return {
        "device_id": device_id,
        "date": start_of_day.date().isoformat(),
        "gross_energy_wh": round(
            gross_energy_wh,
            3,
        ),
        "servo_energy_wh": round(
            servo_energy_wh,
            3,
        ),
        "net_energy_wh": round(
            gross_energy_wh
            - servo_energy_wh,
            3,
        ),
        "sample_count": len(rows),
    }


def get_energy_history(
    db: Session,
    device_id: str,
    days: int,
) -> dict:
    now = datetime.now(timezone.utc)
    since = now - timedelta(days=days)

    rows = _rows_since(
        db,
        device_id,
        since,
    )

    daily: dict[str, list[Telemetry]] = {}

    for row in rows:
        key = row.timestamp.date().isoformat()
        daily.setdefault(key, []).append(row)

    daily_totals = []
    total_energy_wh = 0.0

    for day, day_rows in sorted(
        daily.items()
    ):
        day_rows_sorted = sorted(
            day_rows,
            key=lambda row: row.timestamp,
        )

        energy = _trapezoidal_energy_wh(
            day_rows_sorted
        )

        total_energy_wh += energy

        daily_totals.append(
            {
                "date": day,
                "energy_wh": round(
                    energy,
                    3,
                ),
                "sample_count": len(
                    day_rows_sorted
                ),
            }
        )

    return {
        "device_id": device_id,
        "days": days,
        "total_energy_wh": round(
            total_energy_wh,
            3,
        ),
        "daily": daily_totals,
    }


def get_fixed_vs_adaptive_comparison(
    db: Session,
    device_id: str,
    days: int,
) -> dict:
    """
    Compares fixed vs adaptive operation.

    This comparison is meaningful only when both modes have
    been run under comparable wind conditions.
    """

    now = datetime.now(timezone.utc)
    since = now - timedelta(days=days)

    rows = _rows_since(
        db,
        device_id,
        since,
    )

    fixed_rows = sorted(
        [
            row
            for row in rows
            if row.mode == "fixed"
        ],
        key=lambda row: row.timestamp,
    )

    adaptive_rows = sorted(
        [
            row
            for row in rows
            if row.mode == "adaptive"
        ],
        key=lambda row: row.timestamp,
    )

    fixed_energy_wh = _trapezoidal_energy_wh(
        fixed_rows
    )

    adaptive_energy_wh = _trapezoidal_energy_wh(
        adaptive_rows
    )

    adaptive_servo_energy_wh = sum(
        row.servo_energy_wh
        for row in adaptive_rows
    )

    additional_energy_wh = (
        adaptive_energy_wh
        - fixed_energy_wh
    )

    net_energy_gain_wh = (
        additional_energy_wh
        - adaptive_servo_energy_wh
    )

    improvement_percent = None

    if fixed_energy_wh > 0:
        improvement_percent = round(
            (
                additional_energy_wh
                / fixed_energy_wh
            )
            * 100,
            2,
        )

    return {
        "device_id": device_id,
        "days": days,
        "fixed_energy_wh": round(
            fixed_energy_wh,
            3,
        ),
        "adaptive_energy_wh": round(
            adaptive_energy_wh,
            3,
        ),
        "additional_energy_wh": round(
            additional_energy_wh,
            3,
        ),
        "servo_energy_consumed_wh": round(
            adaptive_servo_energy_wh,
            3,
        ),
        "net_energy_gain_wh": round(
            net_energy_gain_wh,
            3,
        ),
        "improvement_percent": improvement_percent,
        "fixed_sample_count": len(
            fixed_rows
        ),
        "adaptive_sample_count": len(
            adaptive_rows
        ),
        "note": (
            "Estimate based on collected telemetry, "
            "not a certified lab measurement. Needs "
            "comparable wind conditions across both "
            "modes to be meaningful."
        ),
    }
