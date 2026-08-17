"""
VAYUNEXA Control API

Receives safe flap commands from the AI/control layer
and exposes the latest command for the ESP8266/simulator.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.dependencies import verify_api_token
from app.db.database import get_db
from app.services import control_service
from app.services.telemetry_service import get_latest_telemetry


router = APIRouter(
    prefix="/control",
    tags=["control"],
)


class FlapCommandIn(BaseModel):
    device_id: str = "VAYU-001"

    flap_angle_1: float = Field(ge=5, le=35)
    flap_angle_2: float = Field(ge=5, le=35)
    flap_angle_3: float = Field(ge=5, le=35)

    source: str = "ai"


class FlapCommandOut(BaseModel):
    device_id: str
    flap_angle_1: float
    flap_angle_2: float
    flap_angle_3: float
    source: str
    safety_status: str


@router.post(
    "/command",
    response_model=FlapCommandOut,
    dependencies=[Depends(verify_api_token)],
)
def send_control_command(
    payload: FlapCommandIn,
    db: Session = Depends(get_db),
):
    latest = get_latest_telemetry(
        db,
        payload.device_id,
    )

    if latest is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No telemetry found for "
                f"device_id={payload.device_id}"
            ),
        )

    current_angles = (
        latest.flap_angle_1,
        latest.flap_angle_2,
        latest.flap_angle_3,
    )

    target_angles = (
        payload.flap_angle_1,
        payload.flap_angle_2,
        payload.flap_angle_3,
    )

    command = control_service.create_safe_command(
        device_id=payload.device_id,
        current_angles=current_angles,
        target_angles=target_angles,
        source=payload.source,
    )

    return FlapCommandOut(
        device_id=command.device_id,
        flap_angle_1=command.flap_angle_1,
        flap_angle_2=command.flap_angle_2,
        flap_angle_3=command.flap_angle_3,
        source=command.source,
        safety_status=command.safety_status,
    )


@router.get(
    "/latest",
    response_model=FlapCommandOut,
    dependencies=[Depends(verify_api_token)],
)
def get_latest_control_command(
    device_id: str = "VAYU-001",
):
    command = control_service.get_latest_command(
        device_id
    )

    if command is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No control command found for "
                f"device_id={device_id}"
            ),
        )

    return FlapCommandOut(
        device_id=command.device_id,
        flap_angle_1=command.flap_angle_1,
        flap_angle_2=command.flap_angle_2,
        flap_angle_3=command.flap_angle_3,
        source=command.source,
        safety_status=command.safety_status,
    )