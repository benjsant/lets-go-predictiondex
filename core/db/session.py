"""
Database session configuration
===============================

This module configures the SQLAlchemy engine and session factory
used throughout the application.

Responsibilities:
- Read database connection parameters from environment variables
  (Docker- and development-friendly)
- Build the SQLAlchemy database URL
- Initialize a synchronous SQLAlchemy engine
- Expose a `SessionLocal` factory for creating database sessions

This module is intentionally lightweight and does not contain
any business logic. It is consumed by:
- API routes
- Service layers
- ETL / data ingestion scripts
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

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
    """
    FastAPI dependency to get a SQLAlchemy session.
    Usage: db: Session = Depends(get_db)
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
