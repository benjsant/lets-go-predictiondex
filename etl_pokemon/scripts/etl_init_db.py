# app/scripts/etl_init_db.py
"""
ETL - Database initialization script (Pokémon Let's Go)

This script initializes the relational database used by the ETL pipeline
and the API layer of the Pokémon Let's Go project.

Its purpose is to guarantee that:
- All SQLAlchemy models are properly registered
- The full database schema is created in a consistent and reproducible way
- Mandatory reference tables contain required initial data

This script represents the foundation of the ETL process and must be
executed before any data ingestion or transformation steps.

Execution contexts:
- Local development setup
- Containerized environments (Docker / Docker Compose)
- CI/CD pipelines
- Database reset or re-initialization

ETL phase:
- Initialization (pre-Load)

Competency block:
- E1: Relational data modeling, schema initialization, and controlled
      insertion of reference data
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from core.db.base import Base

# ======================================================
# ⚠️ MANDATORY IMPORT OF ALL MODELS
# ======================================================
"""
All SQLAlchemy models must be imported before calling
Base.metadata.create_all().

This ensures:
- Proper table registration
- Correct foreign key resolution
- Complete schema generation

Failure to import a model here would result in missing tables
or broken relationships in the database.
"""

# --- Pokémon domain ---
from core.models.pokemon_species import PokemonSpecies
from core.models.pokemon import Pokemon
from core.models.pokemon_stat import PokemonStat
from core.models.pokemon_type import PokemonType
from core.models.pokemon_move import PokemonMove

# --- Moves domain ---
from core.models.move import Move
from core.models.learn_method import LearnMethod

# --- Types domain ---
from core.models.type import Type
from core.models.type_effectiveness import TypeEffectiveness
from core.models.form import Form
from core.models.move_category import MoveCategory


# ======================================================
# Database environment configuration
# ======================================================
"""
Database connection parameters are resolved from environment variables.

Default values are provided to:
- Enable local development without manual configuration
- Ensure compatibility with Docker Compose deployments
- Maintain portability across environments

The database used is PostgreSQL.
"""

DB_USER = os.getenv("POSTGRES_USER", "letsgo_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "letsgo_password")
DB_HOST = os.getenv("POSTGRES_HOST", "letsgo_postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "letsgo_db")

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

print(f"🔗 Connecting to database at {DB_HOST}:{DB_PORT} / DB: {DB_NAME}")

engine = create_engine(
    DATABASE_URL,
    echo=True,   # Enables SQL logging (useful for dev and CI)
    future=True
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

The LearnMethod table represents a controlled vocabulary describing
how a Pokémon can learn a move (e.g. level up, CT, tutor).

Characteristics:
- Static reference data
- Required for Pokémon ↔ Move relationships
- Inserted only if missing to preserve idempotency
"""

print("📌 Initializing reference data (LearnMethod)...")

methods = ["level_up", "ct", "move_tutor", "before_evolution"]

with Session(engine) as session:
    for name in methods:
        exists = session.query(LearnMethod).filter_by(name=name).first()
        if not exists:
            session.add(LearnMethod(name=name))
    session.commit()

print("✅ LearnMethod initialized")

print("📌 Initializing reference data (Forms)...")

standard_forms = ["base", "mega", "alola", "starter"]

with Session(engine) as session:
    for name in standard_forms:
        exists = session.query(Form).filter_by(name=name).first()
        if not exists:
            session.add(Form(name=name))
    session.commit()

print("✅ Forms initialized")

print("📌 Initializing reference data (Move Categories)...")

move_categories = ["physique", "spécial", "autre"]

with Session(engine) as session:
    for name in move_categories:
        exists = session.query(MoveCategory).filter_by(name=name).first()
        if not exists:
            session.add(MoveCategory(name=name))
    session.commit()

print("✅ Move Categories initialized")
