"""
ETL – Database initialization script (Pokémon Let's Go).

This script initializes the relational database used by the ETL pipeline
and the API layer of the Pokémon Let's Go project.

Responsibilities
----------------
- Ensure all SQLAlchemy models are registered
- Create the full database schema in a reproducible way
- Insert mandatory reference data required by downstream ETL steps

Execution Contexts
------------------
- Local development
- Containerized environments (Docker / Docker Compose)
- CI/CD pipelines
- Database reset or re-initialization

ETL Phase
---------
Initialization (pre-Load)

Competency Scope
----------------
- E1: Relational data modeling, schema initialization,
      and controlled insertion of reference data
"""

from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from core.db.base import Base
from core.models.form import Form
from core.models.learn_method import LearnMethod
from core.models.move_category import MoveCategory


# ======================================================
# ⚠️ MANDATORY MODEL REGISTRATION
# ======================================================
"""
All SQLAlchemy models must be imported before calling
Base.metadata.create_all().

This guarantees:
- Proper table registration
- Correct foreign key resolution
- Complete schema generation

Failure to import a model here would result in missing tables
or broken relationships in the database.
"""

# NOTE:
# Other domain models are imported transitively via Base metadata
# or explicitly loaded by downstream ETL scripts.


# ======================================================
# Database environment configuration
# ======================================================
"""
Database connection parameters are resolved from environment variables.

Default values are provided to:
- Enable local development without manual configuration
- Ensure compatibility with Docker Compose deployments
- Maintain portability across environments

The database engine used is PostgreSQL.
"""

DB_USER = os.getenv("POSTGRES_USER", "letsgo_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "letsgo_password")
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "letsgo_db")

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

print(f"🔗 Connecting to database at {DB_HOST}:{DB_PORT} / DB: {DB_NAME}")

engine = create_engine(
    DATABASE_URL,
    echo=True,   # SQL logging (useful for dev and CI)
    future=True,
)


# ======================================================
# Database schema creation
# ======================================================
"""
Create all database tables defined in the SQLAlchemy metadata.

Behavior:
- Idempotent: existing tables are preserved
- Missing tables are created automatically
- Constraints and relationships are applied

This step must be executed before any ETL load script.
"""

print("🛠️ Creating database schema...")
Base.metadata.create_all(bind=engine)
print("✅ Tables created")


# ======================================================
# Reference data initialization
# ======================================================
"""
Insert mandatory reference data required by downstream ETL processes.

These tables contain static, controlled vocabularies and must exist
before loading Pokémon, moves, or relationships.

Insertion logic is idempotent:
- Data is inserted only if missing
- Existing rows are preserved
"""

# ------------------------------------------------------
# LearnMethod
# ------------------------------------------------------
print("📌 Initializing reference data (LearnMethod)...")

LEARN_METHODS = ["level_up", "ct", "move_tutor", "before_evolution"]

with Session(engine) as session:
    for name in LEARN_METHODS:
        exists = session.query(LearnMethod).filter_by(name=name).first()
        if not exists:
            session.add(LearnMethod(name=name))
    session.commit()

print("✅ LearnMethod initialized")


# ------------------------------------------------------
# Forms
# ------------------------------------------------------
print("📌 Initializing reference data (Forms)...")

STANDARD_FORMS = ["base", "mega", "alola", "starter"]

with Session(engine) as session:
    for name in STANDARD_FORMS:
        exists = session.query(Form).filter_by(name=name).first()
        if not exists:
            session.add(Form(name=name))
    session.commit()

print("✅ Forms initialized")


# ------------------------------------------------------
# Move Categories
# ------------------------------------------------------
print("📌 Initializing reference data (Move Categories)...")

MOVE_CATEGORIES = ["physique", "spécial", "autre"]

with Session(engine) as session:
    for name in MOVE_CATEGORIES:
        exists = session.query(MoveCategory).filter_by(name=name).first()
        if not exists:
            session.add(MoveCategory(name=name))
    session.commit()

print("✅ Move Categories initialized")
