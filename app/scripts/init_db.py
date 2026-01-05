# app/init_db.py
import os
from sqlalchemy import create_engine
from app.db.base import Base

# ======================================================
# ⚠️ IMPORT OBLIGATOIRE DE TOUS LES MODELS
# ======================================================

# --- Pokémon ---
from app.models.pokemon_species import PokemonSpecies
from app.models.pokemon import Pokemon
from app.models.pokemon_stat import PokemonStat
from app.models.pokemon_type import PokemonType
from app.models.pokemon_move import PokemonMove

# --- Moves ---
from app.models.move import Move
from app.models.learn_method import LearnMethod

# --- Types ---
from app.models.type import Type
from app.models.type_effectiveness import TypeEffectiveness


# ======================================================
# Variables d'environnement DB
# ======================================================
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
    echo=True,           # utile en dev / CI
    future=True
)

# ======================================================
# Création des tables
# ======================================================
print("🛠️ Creating database schema...")

Base.metadata.create_all(bind=engine)

print("✅ Toutes les tables ont été créées avec succès !")
