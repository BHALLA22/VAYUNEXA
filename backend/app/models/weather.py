"""
FILE: backend/app/models/weather.py

PURPOSE:
SQLAlchemy ORM model for the "weather" table.

Stores current-condition snapshots and forecast points from
the configured weather provider.
"""

from datetime import datetime, timezone

from sqlalchemy import Float, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Weather(Base):
    __tablename__ = "weather"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    # "current" | "forecast"
    record_type: Mapped[str] = mapped_column(
        String(16),
        default="current",
        index=True,
    )

    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    valid_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
    )

    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)

    wind_speed: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    wind_direction: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    temperature: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    humidity: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    pressure: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    precipitation: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    cloud_cover: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    source: Mapped[str] = mapped_column(
        String(32),
        default="open-meteo",
    )
