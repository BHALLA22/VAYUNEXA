"""
FILE: backend/app/schemas/turbine.py

PURPOSE:
Pydantic schemas for turbine list/detail responses and flap
command requests.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TurbineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: str
    name: str
    location: str | None
    status: str
    mode: str
    created_at: datetime


class FlapCommandIn(BaseModel):
    """
    Manually override flap angles.

    The ESP8266 still re-validates these against its own safety
    limits before moving any servo.
    """

    flap_angle_1: float = Field(..., ge=0, le=90)
    flap_angle_2: float = Field(..., ge=0, le=90)
    flap_angle_3: float = Field(..., ge=0, le=90)

    reason: str = Field(
        default="manual override",
    )


class FlapCommandOut(BaseModel):
    status: str
    turbine_id: int
    commanded_angles: list[float]
    note: str
