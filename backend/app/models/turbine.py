"""
FILE: backend/app/models/turbine.py

PURPOSE:
SQLAlchemy ORM model for the "turbines" table.
"""

from datetime import datetime, timezone

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Turbine(Base):
    __tablename__ = "turbines"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    device_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(128),
        default="VayuNex Turbine",
    )

    location: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        default="offline",
    )

    mode: Mapped[str] = mapped_column(
        String(32),
        default="adaptive",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    telemetry_readings = relationship(
        "Telemetry",
        back_populates="turbine",
        cascade="all, delete-orphan",
    )

    forecasts = relationship(
        "Forecast",
        back_populates="turbine",
        cascade="all, delete-orphan",
    )
