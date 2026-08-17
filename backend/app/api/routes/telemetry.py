"""
FILE: backend/app/api/routes/telemetry.py
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_db,
    verify_api_token,
)
from app.schemas.telemetry import (
    TelemetryIn,
    TelemetryOut,
    TelemetryIngestResponse,
)
from app.services import telemetry_service


router = APIRouter(
    prefix="/telemetry",
    tags=["telemetry"],
)


@router.post(
    "",
    response_model=TelemetryIngestResponse,
    dependencies=[Depends(verify_api_token)],
)
def post_telemetry(
    payload: TelemetryIn,
    db: Session = Depends(get_db),
):
    record = telemetry_service.ingest_telemetry(
        db,
        payload,
    )

    return TelemetryIngestResponse(
        status="stored",
        telemetry_id=record.id,
        calculated_power_watts=record.power,
    )


@router.get(
    "/latest",
    response_model=TelemetryOut,
)
def get_latest(
    device_id: str = Query(...),
    db: Session = Depends(get_db),
):
    record = telemetry_service.get_latest_telemetry(
        db,
        device_id,
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No telemetry found for "
                f"device_id={device_id}"
            ),
        )

    return record


@router.get(
    "/history",
    response_model=list[TelemetryOut],
)
def get_history(
    device_id: str = Query(...),
    hours: int = Query(
        24,
        ge=1,
        le=24 * 30,
    ),
    db: Session = Depends(get_db),
):
    return telemetry_service.get_telemetry_history(
        db,
        device_id,
        hours,
    )
