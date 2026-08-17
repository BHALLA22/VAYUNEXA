"""
FILE: backend/app/db/init_db.py

PURPOSE:
Creates every table in PostgreSQL from the SQLAlchemy models.
"""

from app.db.database import Base, engine

# Import the model package so every ORM class is registered.
import app.models  # noqa: F401


def init_db() -> None:
    print("Creating tables...")

    Base.metadata.create_all(bind=engine)

    print(
        f"Tables created: {list(Base.metadata.tables.keys())}"
    )

    print("Done.")


if __name__ == "__main__":
    init_db()
