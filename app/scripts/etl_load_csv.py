"""
ETL – CSV Data Loading into Relational Database (Pokémon Let's Go)

Overview
--------
This script implements the core deterministic ETL pipeline of the project.
It loads structured CSV reference data into the relational database and
establishes the foundational dataset used by all downstream processes.

Data Sources
------------
The script consumes the following CSV files:
- liste_pokemon.csv          : Pokémon species, forms, and types
- liste_capacite_lets_go.csv : Pokémon moves and attributes
- table_type.csv             : Type effectiveness matrix

ETL Responsibilities
--------------------
- Extract structured data from CSV files
- Normalize raw values (booleans, integers, string keys)
- Apply business rules (Pokémon forms, type slots)
- Persist data using idempotent upsert guards
- Ensure referential integrity between entities

Design Principles
-----------------
- CSV files are the authoritative and reproducible data source
- No external API is involved in this step
- The ETL is deterministic and safely re-runnable
- Database writes are idempotent (no duplicates)

Competency Scope (E1)
---------------------
This script fully addresses competency block E1 by demonstrating:
- structured data extraction
- transformation and normalization
- relational data modeling
- controlled loading into a SQL database

This script intentionally avoids orchestration frameworks
and advanced MLOps tooling, which are outside the E1 scope.

Execution Context
-----------------
This script must be executed after:
- database schema initialization

It must be executed before:
- external API enrichment
- web scraping
- machine learning pipelines

Usage
-----
python app/scripts/etl_load_csv.py
"""

import csv
from decimal import Decimal

# Ensures all SQLAlchemy models are registered
import app.models  # noqa: F401

from app.db.session import SessionLocal
from app.models import (
    PokemonSpecies,
    PokemonType,
    TypeEffectiveness,
)
from app.db.guards.type import upsert_type
from app.db.guards.move import upsert_move
from app.db.guards.pokemon import upsert_pokemon


DATA_PATH = "data/csv"


# ---------------------------------------------------------------------
# Normalization Helpers
# ---------------------------------------------------------------------
def normalize_bool(value):
    """
    Normalize boolean-like CSV values.

    Accepted truthy values (case-insensitive):
    - "1", "true", "yes", "oui"

    Parameters
    ----------
    value : Any
        Raw CSV value.

    Returns
    -------
    bool
        Normalized boolean value.
    """
    return str(value).strip().lower() in ("1", "true", "yes", "oui")


def normalize_int(value):
    """
    Normalize optional integer CSV values.

    Empty strings and None values are converted to None.

    Parameters
    ----------
    value : str | None
        Raw CSV value.

    Returns
    -------
    int | None
        Normalized integer or None.
    """
    return int(value) if value not in ("", None) else None


def normalize_key(value: str) -> str:
    """
    Normalize string keys for consistent lookups.

    Operations:
    - trim leading and trailing spaces
    - convert to lowercase

    Parameters
    ----------
    value : str
        Raw string value.

    Returns
    -------
    str
        Normalized key.
    """
    return value.strip().lower()


# ---------------------------------------------------------------------
# Load TYPES
# ---------------------------------------------------------------------
def load_types(session):
    """
    Extract and load Pokémon elemental types.

    Types are inferred from Pokémon CSV columns (type_1, type_2)
    and deduplicated before insertion.

    Parameters
    ----------
    session : Session
        SQLAlchemy database session.
    """
    print("➡ Loading types...")

    seen = set()

    with open(f"{DATA_PATH}/liste_pokemon.csv", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            for col in ("type_1", "type_2"):
                name = row.get(col)
                if not name:
                    continue

                key = normalize_key(name)
                if key in seen:
                    continue

                upsert_type(session, name=name.strip())
                seen.add(key)

    session.commit()
    print(f"✔ {len(seen)} types inserted")


# ---------------------------------------------------------------------
# Load MOVES
# ---------------------------------------------------------------------
def load_moves(session):
    """
    Extract and load Pokémon moves.

    Each move is associated with:
    - a type
    - a category
    - optional power and accuracy values

    Parameters
    ----------
    session : Session
        SQLAlchemy database session.
    """
    print("➡ Loading moves...")

    type_map = {
        normalize_key(t.name): t.id
        for t in session.query(app.models.Type).all()
    }

    with open(f"{DATA_PATH}/liste_capacite_lets_go.csv", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            upsert_move(
                session,
                name=row["nom_français"].strip(),
                type_id=type_map[normalize_key(row["type"])],
                category=row["classe"].strip(),
                power=normalize_int(row.get("puissance")),
                accuracy=normalize_int(row.get("précision")),
                description=row.get("description"),
                damage_type=row.get("type_degats") or None,
            )

    session.commit()
    print("✔ Moves inserted")


# ---------------------------------------------------------------------
# Load POKÉMON SPECIES
# ---------------------------------------------------------------------
def load_pokemon_species(session):
    """
    Load Pokémon species reference data.

    Species data represents the canonical Pokédex entity,
    independent of forms or variants.

    Parameters
    ----------
    session : Session
        SQLAlchemy database session.
    """
    print("➡ Loading pokemon species...")

    with open(f"{DATA_PATH}/liste_pokemon.csv", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            species = PokemonSpecies(
                id=int(row["id"]),
                pokedex_number=int(row["num_pokedex"]),
                name_fr=row["nom_fr"].strip(),
                name_en=row.get("nom_eng"),
            )
            session.merge(species)

    session.commit()
    print("✔ Pokemon species inserted")


# ---------------------------------------------------------------------
# Load POKÉMON FORMS
# ---------------------------------------------------------------------
def load_pokemon(session):
    """
    Load Pokémon forms and variants.

    Business rules:
    - A Pokémon species may have multiple forms
    - Forms include: base, mega, alola, starter
    - Physical attributes are initialized and enriched later

    Parameters
    ----------
    session : Session
        SQLAlchemy database session.
    """
    print("➡ Loading pokemon forms...")

    with open(f"{DATA_PATH}/liste_pokemon.csv", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            pokemon_id = int(row["id"])

            is_mega = normalize_bool(row.get("mega"))
            is_alola = normalize_bool(row.get("alola"))
            is_starter = normalize_bool(row.get("starter"))

            if is_mega:
                form_name = "mega"
            elif is_alola:
                form_name = "alola"
            elif is_starter:
                form_name = "starter"
            else:
                form_name = "base"

            upsert_pokemon(
                session,
                species_id=pokemon_id,
                form_name=form_name,
                name_pokeapi=row.get("nom_pokeapi"),
                name_pokepedia=row.get("nom_pokepedia"),
                is_mega=is_mega,
                is_alola=is_alola,
                is_starter=is_starter,
                height_m=Decimal("0.00"),
                weight_kg=Decimal("0.00"),
                sprite_url=None,
            )

    session.commit()
    print("✔ Pokemon forms inserted")


# ---------------------------------------------------------------------
# Load POKÉMON ↔ TYPES
# ---------------------------------------------------------------------
def load_pokemon_types(session):
    """
    Associate Pokémon forms with their elemental types.

    Supports mono-type and dual-type Pokémon with ordered slots.

    Parameters
    ----------
    session : Session
        SQLAlchemy database session.
    """
    print("➡ Loading pokemon types...")

    type_map = {
        normalize_key(t.name): t.id
        for t in session.query(app.models.Type).all()
    }

    with open(f"{DATA_PATH}/liste_pokemon.csv", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            pokemon_id = int(row["id"])

            if row.get("type_1"):
                session.merge(
                    PokemonType(
                        pokemon_id=pokemon_id,
                        type_id=type_map[normalize_key(row["type_1"])],
                        slot=1,
                    )
                )

            if row.get("type_2"):
                session.merge(
                    PokemonType(
                        pokemon_id=pokemon_id,
                        type_id=type_map[normalize_key(row["type_2"])],
                        slot=2,
                    )
                )

    session.commit()
    print("✔ Pokemon types inserted")


# ---------------------------------------------------------------------
# Load TYPE EFFECTIVENESS
# ---------------------------------------------------------------------
def load_type_effectiveness(session):
    """
    Load type effectiveness multipliers.

    Defines damage multipliers between attacking and defending types.

    Parameters
    ----------
    session : Session
        SQLAlchemy database session.
    """
    print("➡ Loading type effectiveness...")

    type_map = {
        normalize_key(t.name): t.id
        for t in session.query(app.models.Type).all()
    }

    with open(f"{DATA_PATH}/table_type.csv", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            effectiveness = TypeEffectiveness(
                attacking_type_id=type_map[normalize_key(row["type_attaquant"])],
                defending_type_id=type_map[normalize_key(row["type_defenseur"])],
                multiplier=Decimal(row["multiplicateur"]),
            )
            session.merge(effectiveness)

    session.commit()
    print("✔ Type effectiveness inserted")


# ---------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------
def main():
    """
    Execute the CSV ETL pipeline.

    Loading order is enforced to preserve referential integrity:
    1. Types
    2. Moves
    3. Pokémon species
    4. Pokémon forms
    5. Pokémon ↔ Types associations
    6. Type effectiveness
    """
    session = SessionLocal()
    try:
        load_types(session)
        load_moves(session)
        load_pokemon_species(session)
        load_pokemon(session)
        load_pokemon_types(session)
        load_type_effectiveness(session)
    finally:
        session.close()


if __name__ == "__main__":
    main()
