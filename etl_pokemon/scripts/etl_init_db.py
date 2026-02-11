"""Database initialization script for the ETL pipeline."""

from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from core.db.base import Base
from core.models.form import Form
from core.models.learn_method import LearnMethod
from core.models.move_category import MoveCategory


# Database environment configuration
DB_USER = os.getenv("POSTGRES_USER", "letsgo_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "letsgo_password")
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "letsgo_db")

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

print(f" Connecting to database at {DB_HOST}:{DB_PORT} / DB: {DB_NAME}")

engine = create_engine(
    DATABASE_URL,
    echo=True, # SQL logging (useful for dev and CI)
    future=True,
)


# Create database schema
print(" Creating database schema...")
Base.metadata.create_all(bind=engine)
print("Tables created")


# Reference data initialization
print(" Initializing reference data (LearnMethod)...")

LEARN_METHODS = ["level_up", "ct", "move_tutor", "before_evolution"]

with Session(engine) as session:
    for name in LEARN_METHODS:
        exists = session.query(LearnMethod).filter_by(name=name).first()
        if not exists:
            session.add(LearnMethod(name=name))
    session.commit()

print("LearnMethod initialized")


# Forms
print(" Initializing reference data (Forms)...")

STANDARD_FORMS = ["base", "mega", "alola", "starter"]

with Session(engine) as session:
    for name in STANDARD_FORMS:
        exists = session.query(Form).filter_by(name=name).first()
        if not exists:
            session.add(Form(name=name))
    session.commit()

print("Forms initialized")


# Move Categories
print(" Initializing reference data (Move Categories)...")

MOVE_CATEGORIES = ["physique", "spécial", "autre"]

with Session(engine) as session:
    for name in MOVE_CATEGORIES:
        exists = session.query(MoveCategory).filter_by(name=name).first()
        if not exists:
            session.add(MoveCategory(name=name))
    session.commit()

print("Move Categories initialized")
