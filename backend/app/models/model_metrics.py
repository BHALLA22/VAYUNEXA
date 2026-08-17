"""
FILE: backend/app/models/model_metrics.py

PURPOSE:
SQLAlchemy ORM model for the "model_metrics" table.

Stores metrics for each trained AI model version.
"""

from datetime import datetime, timezone

from sqlalchemy import Float, String, DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class ModelMetrics(Base):
    __tablename__ = "model_metrics"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    model_version: Mapped[str] = mapped_column(
        String(64),
        index=True,
    )

    # Mean Absolute Error
    mae: Mapped[float] = mapped_column(Float)

    # Root Mean Squared Error
    rmse: Mapped[float] = mapped_column(Float)

    # R-squared
    r2: Mapped[float] = mapped_column(Float)

    # Mean Absolute Percentage Error
    mape: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    training_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    dataset_size: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
