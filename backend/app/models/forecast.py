"""
FILE: backend/app/models/forecast.py

PURPOSE:
SQLAlchemy ORM model for the "forecasts" table.

Each row represents one hourly energy prediction produced by
the AI model or fallback heuristic.
"""

from datetime import datetime, timezone

from sqlalchemy import Float, String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Forecast(Base):
    __tablename__ = "forecasts"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    turbine_id: Mapped[int] = mapped_column(
        ForeignKey("turbines.id"),
        index=True,
    )

    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    forecast_for: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
    )

    predicted_energy_wh: Mapped[float] = mapped_column(Float)

    horizon_hours: Mapped[int] = mapped_column(Integer)

    model_version: Mapped[str] = mapped_column(
        String(64),
        default="heuristic-fallback",
    )

    turbine = relationship(
        "Turbine",
        back_populates="forecasts",
    )
