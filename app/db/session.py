import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# --------------------
# Paramètres DB (Docker / Dev friendly)
# --------------------
DB_USER = os.getenv("POSTGRES_USER", "letsgo_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "letsgo_password")
DB_HOST = os.getenv("POSTGRES_HOST", "letsgo_postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "letsgo_db")

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# --------------------
# Engine SQLAlchemy (sync)
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
