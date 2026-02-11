"""SQLAlchemy engine and session factory configuration."""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# --------------------
# Database parameters (Docker / Dev friendly)
# --------------------
DB_USER = os.getenv("POSTGRES_USER", "letsgo_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "letsgo_password")
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "letsgo_db")

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# --------------------
# SQLAlchemy engine (synchronous)
# --------------------
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

# --------------------
# Session factory
# --------------------
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    """FastAPI dependency that yields a database session."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
