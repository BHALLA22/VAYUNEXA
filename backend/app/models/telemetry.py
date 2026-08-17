"""
FILE: backend/app/models/telemetry.py

PURPOSE:
SQLAlchemy ORM model for the "telemetry" table.

One row represents one reading sent by the ESP8266 or simulator.
Power is ALWAYS calculated on the backend as P = V × I.
"""

from datetime import datetime, timezone

from sqlalchemy import Float, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Telemetry(Base):
    __tablename__ = "telemetry"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    turbine_id: Mapped[int] = mapped_column(
        ForeignKey("turbines.id"),
        index=True,
    )

    device_id: Mapped[str] = mapped_column(
        String(64),
        index=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    wind_speed: Mapped[float] = mapped_column(Float)
    wind_direction: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    rpm: Mapped[float] = mapped_column(Float)

    voltage: Mapped[float] = mapped_column(Float)
    current: Mapped[float] = mapped_column(Float)

    # Server-calculated: voltage × current
    power: Mapped[float] = mapped_column(Float)

    flap_angle_1: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    flap_angle_2: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    flap_angle_3: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    temperature: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    humidity: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    mode: Mapped[str] = mapped_column(
        String(32),
        default="adaptive",
    )

    servo_energy_wh: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    turbine = relationship(
        "Turbine",
        back_populates="telemetry_readings",
    )
