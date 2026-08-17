from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.services.auto_controller import calculate_control_decision


router = APIRouter(
    prefix="/control",
    tags=["control"],
)

API_KEY = "dev-token-change-me"


class ControlCommand(BaseModel):
    device_id: str = Field(
        min_length=1,
        description="Target turbine device ID",
    )

    flap_angle_1: float = Field(
        ge=5,
        le=35,
    )

    flap_angle_2: float = Field(
        ge=5,
        le=35,
    )

    flap_angle_3: float = Field(
        ge=5,
        le=35,
    )

    source: str = Field(
        default="ai",
    )


class AutoControlRequest(BaseModel):
    device_id: str = Field(
        min_length=1,
    )


@router.post("/command")
def send_control_command(
    command: ControlCommand,
    x_api_key: str | None = Header(default=None),
):
    """
    Accept a manual/AI flap-control command.
    """

    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
        )

    angles = [
        command.flap_angle_1,
        command.flap_angle_2,
        command.flap_angle_3,
    ]

    if any(angle < 5 or angle > 35 for angle in angles):
        raise HTTPException(
            status_code=400,
            detail="Flap angles must be between 5 and 35 degrees",
        )

    return {
        "status": "accepted",
        "device_id": command.device_id,
        "flap_angle_1": round(command.flap_angle_1, 1),
        "flap_angle_2": round(command.flap_angle_2, 1),
        "flap_angle_3": round(command.flap_angle_3, 1),
        "source": command.source,
        "servo_status": "ready",
        "message": "Flap control command accepted",
    }


@router.post("/auto")
def automatic_control(
    request: AutoControlRequest,
    db: Session = Depends(get_db),
    x_api_key: str | None = Header(default=None),
):
    """
    Automatic VAYUNEXA flap controller.

    Latest telemetry
          ↓
    Optimization engine
          ↓
    Safety limits
          ↓
    Target angles
    """

    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
        )

    try:
        decision = calculate_control_decision(
            db=db,
            device_id=request.device_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except Exception as error:
        print(
            f"[AUTO CONTROL ERROR] {type(error).__name__}: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Internal server error. "
                "Check server logs for details."
            ),
        )

    return {
        "status": "accepted",
        "device_id": decision.device_id,
        "source": "ai",
        "control_mode": "AUTO",

        "current_angles": {
            "flap_1": round(
                decision.current_angles[0],
                1,
            ),
            "flap_2": round(
                decision.current_angles[1],
                1,
            ),
            "flap_3": round(
                decision.current_angles[2],
                1,
            ),
        },

        "target_angles": {
            "flap_1": round(
                decision.target_angles[0],
                1,
            ),
            "flap_2": round(
                decision.target_angles[1],
                1,
            ),
            "flap_3": round(
                decision.target_angles[2],
                1,
            ),
        },

        "reason": decision.reason,

        "expected_power_gain_percent": (
            decision.expected_power_gain_percent
        ),

        "safety_status": (
            "SAFE"
            if decision.safe
            else "UNSAFE"
        ),

        "message": (
            "Automatic flap recommendation calculated "
            "successfully."
        ),
    }