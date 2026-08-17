"""
FILE: backend/tests/conftest.py

PURPOSE:
Shared pytest fixtures.

Tests use an in-memory SQLite database instead of PostgreSQL,
so the test suite requires no Docker or external database.

The application's get_db dependency is overridden to use this
SQLite test database.
"""

import pytest

from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.database import Base, get_db
from app.main import app

# Import all ORM models so SQLAlchemy relationships are registered.
from app.models import (
    forecast,
    model_metrics,
    telemetry,
    turbine,
    weather,
)  # noqa: F401


TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture(
    scope="function",
    autouse=True,
)
def setup_database():
    """
    Create fresh tables for every test and remove them afterwards.
    """

    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)


def override_get_db():
    """
    Provide the SQLite testing session to FastAPI.
    """

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """
    FastAPI TestClient fixture.
    """

    return TestClient(app)


@pytest.fixture
def auth_headers():
    """
    Authentication header used by protected write endpoints.
    """

    return {
        "X-API-Key": settings.api_token,
    }
