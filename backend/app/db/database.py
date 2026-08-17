"""
FILE: backend/app/db/database.py

PURPOSE:
Creates the SQLAlchemy engine + session factory used by every
route. Also defines Base, which every model in app/models/
inherits from.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)


class Base(DeclarativeBase):
    """
    All ORM models (Turbine, Telemetry, Weather, Forecast, ModelMetrics)
    inherit from this class.
    """

    pass


def get_db():
    """
    FastAPI dependency: yields a DB session and always closes it,
    even if the request raises an exception.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
