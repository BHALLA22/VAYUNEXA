"""
FILE: backend/app/services/optimization_service.py

PURPOSE:
Baseline, explainable flap-angle controller.

This is a rule-based controller, NOT a trained ML model.
It provides a safe and understandable starting point.

All thresholds below are prototype/experimental values and
must be tuned using measurements from the actual turbine.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.telemetry import Telemetry


# --- Configurable prototype thresholds ---

CUT_IN_WIND_MS = 2.5
LOW_WIND_MS = 5.0
MID_WIND_MS = 9.0
HIGH_WIND_MS = 13.0
CUT_OUT_WIND_MS = 18.0


# --- Prototype flap angles ---

FLAP_ANGLE_CUT_IN = 5.0
FLAP_ANGLE_LOW = 10.0
FLAP_ANGLE_MID = 18.0
FLAP_ANGLE_HIGH = 27.0
FLAP_ANGLE_SAFETY = 35.0


def _recommend_from_wind_speed(
    wind_speed: float,
) -> tuple[float, str, float]:
    """
    Returns:

        (recommended_angle,
         explanation,
         expected_power_gain_percent_estimate)
    """

    if wind_speed < CUT_IN_WIND_MS:
        return (
            FLAP_ANGLE_CUT_IN,
            "Below cut-in wind speed: minimal flap angle to aid startup torque.",
            2.0,
        )

    if wind_speed < LOW_WIND_MS:
        return (
            FLAP_ANGLE_LOW,
            "Low wind speed: small flap angle to maximize energy capture.",
            5.0,
        )

    if wind_speed < MID_WIND_MS:
        return (
            FLAP_ANGLE_MID,
            "Moderate wind speed: intermediate flap setting balances capture and load.",
            8.4,
        )

    if wind_speed < HIGH_WIND_MS:
        return (
            FLAP_ANGLE_HIGH,
            "High wind speed: increased flap angle to regulate rotor speed.",
            6.0,
        )

    return (
        FLAP_ANGLE_SAFETY,
        "Near/above safety threshold: large flap angle to spill excess wind energy.",
        0.0,
    )


def get_recommendation(
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
            "recommended_angle": FLAP_ANGLE_LOW,
            "current_angle_avg": 0.0,
            "reason": (
                "No telemetry received yet for this device; "
                "returning a safe default angle."
            ),
            "expected_power_gain_percent": 0.0,
            "is_experimental_estimate": True,
            "controller_version": "baseline-rule-v1",
        }

    angle, reason, gain_estimate = (
        _recommend_from_wind_speed(
            latest.wind_speed
        )
    )

    current_avg = (
        latest.flap_angle_1
        + latest.flap_angle_2
        + latest.flap_angle_3
    ) / 3.0

    return {
        "device_id": device_id,
        "recommended_angle": angle,
        "current_angle_avg": round(
            current_avg,
            2,
        ),
        "reason": reason,
        "expected_power_gain_percent": gain_estimate,
        "is_experimental_estimate": True,
        "controller_version": "baseline-rule-v1",
    }
