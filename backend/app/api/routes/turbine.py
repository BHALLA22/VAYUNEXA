"""
FILE: backend/app/api/routes/turbine.py
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_db,
    verify_api_token,
)
from app.models.turbine import Turbine
from app.schemas.turbine import (
    TurbineOut,
    FlapCommandIn,
    FlapCommandOut,
)


router = APIRouter(tags=["turbines"])


@router.get(
    "/turbines",
    response_model=list[TurbineOut],
)
def list_turbines(
    db: Session = Depends(get_db),
):
    return (
        db.query(Turbine)
        .order_by(Turbine.id.asc())
        .all()
    )


@router.get(
    "/turbines/{turbine_id}",
    response_model=TurbineOut,
)
def get_turbine(
    turbine_id: int,
    db: Session = Depends(get_db),
):
    turbine = db.get(
        Turbine,
        turbine_id,
    )

    if turbine is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Turbine id={turbine_id} "
                "not found"
            ),
        )

    return turbine


@router.post(
    "/turbine/{turbine_id}/flap-command",
    response_model=FlapCommandOut,
    dependencies=[Depends(verify_api_token)],
)
def flap_command(
    turbine_id: int,
    payload: FlapCommandIn,
    db: Session = Depends(get_db),
):
    turbine = db.get(
        Turbine,
        turbine_id,
    )

    if turbine is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Turbine id={turbine_id} "
                "not found"
            ),
        )

    angles = [
        payload.flap_angle_1,
        payload.flap_angle_2,
        payload.flap_angle_3,
    ]

    return FlapCommandOut(
        status="accepted",
        turbine_id=turbine_id,
        commanded_angles=angles,
        note=(
            "Command recorded. The ESP8266 must "
            "re-validate angles against its own "
            "hardware safety limits."
        ),
    )
