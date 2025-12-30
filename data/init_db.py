# app/init_db.py
import os
from sqlalchemy import create_engine
from app.db.base import Base  # ✅ Correct import

# Récupérer les variables d'environnement
DB_USER = os.getenv("POSTGRES_USER", "letsgo_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "letsgo_password")
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "letsgo_db")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Créer un engine synchrone pour init DB
engine = create_engine(DATABASE_URL.replace("+asyncpg", ""), echo=True)

# Créer toutes les tables
Base.metadata.create_all(bind=engine)

print("✅ Toutes les tables ont été créées avec succès !")
