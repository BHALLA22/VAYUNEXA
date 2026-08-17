"""
VAYUNEXA AI Prediction API

Provides:
- Current predicted power
- Optimal flap angle
- Candidate angle curve
- Expected power gain
- ML model version
- Experimental status
"""

from fastapi import APIRouter, Header, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.telemetry import Telemetry
from app.services.ai_prediction_service import find_best_flap_angle


router = APIRouter(
    prefix="/ai",
    tags=["ai"],
)


API_KEY = "dev-token-change-me"


@router.get("/prediction")
def get_ai_prediction(
    device_id: str,
    x_api_key: str | None = Header(default=None),
):
    """
    Return the latest ML prediction and optimal flap angle.
    """

    # ---------------------------------------------------------
    # API KEY
    # ---------------------------------------------------------

    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
        )

    # ---------------------------------------------------------
    # DATABASE
    # ---------------------------------------------------------

    db: Session = SessionLocal()

    try:

        latest = db.execute(
            select(Telemetry)
            .where(
                Telemetry.device_id == device_id
            )
            .order_by(
                desc(Telemetry.timestamp)
            )
            .limit(1)
        ).scalar_one_or_none()

        if latest is None:
            raise HTTPException(
                status_code=404,
                detail=f"No telemetry available for {device_id}",
            )

        # -----------------------------------------------------
        # CURRENT FLAP ANGLE
        # -----------------------------------------------------

        current_flap_angle = (
            float(latest.flap_angle_1)
            + float(latest.flap_angle_2)
            + float(latest.flap_angle_3)
        ) / 3.0

        # -----------------------------------------------------
        # ML OPTIMIZATION
        # -----------------------------------------------------

        result = find_best_flap_angle(
            wind_speed=float(latest.wind_speed),
            wind_direction=float(latest.wind_direction),
            rpm=float(latest.rpm),
            temperature=float(latest.temperature),
            humidity=float(latest.humidity),
            current_flap_angle=current_flap_angle,
        )

        # -----------------------------------------------------
        # RESPONSE
        # -----------------------------------------------------

        return {
            "status": "success",
            "device_id": device_id,

            "current_flap_angle": round(
                current_flap_angle,
                2,
            ),

            "optimal_flap_angle": result[
                "recommended_angle"
            ],

            "current_predicted_power_w": result[
                "current_predicted_power_w"
            ],

            "predicted_power_w": result[
                "predicted_power_w"
            ],

            "expected_power_gain_percent": result[
                "expected_power_gain_percent"
            ],

            "candidates": result[
                "candidates"
            ],

            "model_version": result[
                "model_version"
            ],

            "controller_type": result[
                "controller_type"
            ],

            "is_experimental_estimate": True,

            "confidence": "experimental",

            "input_conditions": {
                "wind_speed": round(
                    float(latest.wind_speed),
                    2,
                ),
                "wind_direction": round(
                    float(latest.wind_direction),
                    1,
                ),
                "rpm": round(
                    float(latest.rpm),
                    1,
                ),
                "temperature": round(
                    float(latest.temperature),
                    1,
                ),
                "humidity": round(
                    float(latest.humidity),
                    1,
                ),
            },
        }

    finally:

        db.close()