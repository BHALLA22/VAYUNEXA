"""
FILE: backend/app/schemas/telemetry.py

PURPOSE:
Pydantic request/response models for the telemetry endpoints.
TelemetryIn field names must exactly match the JSON keys sent by
the ESP8266 firmware and the turbine simulator.
"""

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field


class TelemetryIn(BaseModel):
    """What the ESP8266 / simulator POSTs to /api/v1/telemetry."""

    device_id: str = Field(
        ...,
        examples=["WIND-001"],
    )

    timestamp: datetime | None = Field(
        default=None,
        description="If omitted, server time is used.",
    )

    wind_speed: float = Field(
        ...,
        ge=0,
        le=100,
        description="m/s",
    )

    wind_direction: float | None = Field(
        default=None,
        ge=0,
        le=360,
    )

    rpm: float = Field(
        ...,
        ge=0,
        le=20000,
    )

    voltage: float = Field(
        ...,
        ge=0,
        le=1000,
    )

    current: float = Field(
        ...,
        ge=0,
        le=1000,
    )

    flap_angle_1: float = Field(
        ...,
        ge=0,
        le=90,
    )

    flap_angle_2: float = Field(
        ...,
        ge=0,
        le=90,
    )

    flap_angle_3: float = Field(
        ...,
        ge=0,
        le=90,
    )

    temperature: float | None = Field(
        default=None,
        ge=-40,
        le=85,
    )

    humidity: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    mode: str = Field(
        default="adaptive",
        description="adaptive | fixed | safety | simulation",
    )

    def resolved_timestamp(self) -> datetime:
        return self.timestamp or datetime.now(timezone.utc)


class TelemetryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: str
    timestamp: datetime
    wind_speed: float
    wind_direction: float | None
    rpm: float
    voltage: float
    current: float
    power: float
    flap_angle_1: float
    flap_angle_2: float
    flap_angle_3: float
    temperature: float | None
    humidity: float | None
    mode: str
    servo_energy_wh: float


class TelemetryIngestResponse(BaseModel):
    status: str
    telemetry_id: int
    calculated_power_watts: float
