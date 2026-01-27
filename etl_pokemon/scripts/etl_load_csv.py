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

# Ensure all SQLAlchemy models are registered
import core.models  # noqa: F401
from core.db.guards.move import upsert_move
from core.db.guards.pokemon import upsert_pokemon
from core.db.guards.pokemon_type import upsert_pokemon_type
from core.db.guards.type import upsert_type
from core.db.session import SessionLocal
from core.models import (
    Form,
    MoveCategory,
    PokemonSpecies,
    TypeEffectiveness,
)

DATA_PATH = "etl_pokemon/data/csv"


# ---------------------------------------------------------------------
# Normalization Helpers
# ---------------------------------------------------------------------
def normalize_bool(value):
    """Normalize boolean-like CSV values (1, true, yes, oui → True)."""
    return str(value).strip().lower() in ("1", "true", "yes", "oui")


def normalize_int(value):
    """Convert optional integer CSV values, empty string or None → None."""
    return int(value) if value not in ("", None) else None


def normalize_key(value: str) -> str:
    """Normalize string keys: strip spaces and lowercase for consistent lookups."""
    return value.strip().lower()


# ---------------------------------------------------------------------
# Priority Mapping from damage_type
# ---------------------------------------------------------------------
PRIORITY_FROM_DAMAGE_TYPE = {
    # +2: Extreme priority (protection moves and Ruse)
    "protection_change_plusieur": 2,  # Abri
    "prioritaire_deux": 2,            # Ruse (bypasses Abri)

    # +1: High priority (quick attack moves)
    "prioritaire": 1,                 # Vive-Attaque, Aqua-Jet, Éclats Glace
    "prioritaire_conditionnel": 1,    # Coup Bas (fails if enemy doesn't attack)
    "prioritaire_critique": 1,        # Pika-Sprint (priority + guaranteed crit)

    # 0: Normal priority (default)
    "offensif": 0,
    "statut": 0,
    "multi_coups": 0,
    "double_degats": 0,
    "fixe_niveau": 0,
    "fixe_degat_20": 0,
    "fixe_degat_40": 0,
    "fixe_moitie_degats": 0,
    "ko_en_un_coup": 0,
    "soin": 0,
    "variable_degats_poids": 0,
    "sommeil_requis": 0,
    "attk_adversaire": 0,
    "degat_aleatoire": 0,
    "inutile": 0,
    "critique_100": 0,
    "absorption": 0,
    "piege": 0,

    # Two-turn moves: no priority change, but damage is halved in dataset
    "deux_tours": 0,

    # -5: Counter moves (always move after being hit)
    "renvoi_degat_double_physique": -5,
    "renvoi_degat_double_special": -5,
    "renvoi_degat_double_deux_tours": -5,
}


def get_priority_from_damage_type(damage_type: str | None) -> int:
    """Get move priority from damage_type field."""
    if not damage_type:
        return 0
    return PRIORITY_FROM_DAMAGE_TYPE.get(damage_type.strip().lower(), 0)


# ---------------------------------------------------------------------
# Load TYPES
# ---------------------------------------------------------------------
def load_types(session):
    """Extract and load Pokémon elemental types from liste_pokemon.csv."""
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
# Load MOVE CATEGORIES
# ---------------------------------------------------------------------
def load_move_categories(session):
    """Load Pokémon move categories from liste_capacite_lets_go.csv. Categories are assumed initialized."""
    print("➡ Loading move categories...")
    seen = set()
    with open(f"{DATA_PATH}/liste_capacite_lets_go.csv", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = row.get("classe")
            if not name:
                continue
            key = normalize_key(name)
            if key in seen:
                continue
            mc = session.query(MoveCategory).filter_by(name=name.strip()).first()
            if not mc:
                raise ValueError(f"MoveCategory '{name.strip()}' not found in DB. Ensure init_db created it.")
            seen.add(key)
    print(f"✔ {len(seen)} move categories verified")


# ---------------------------------------------------------------------
# Load MOVES
# ---------------------------------------------------------------------
def load_moves(session):
    """Extract and load Pokémon moves with type, category, power, accuracy, and description."""
    print("➡ Loading moves...")
    from core.models import MoveCategory, Type
    type_map = {normalize_key(t.name): t.id for t in session.query(Type).all()}
    category_map = {normalize_key(c.name): c.id for c in session.query(MoveCategory).all()}

    with open(f"{DATA_PATH}/liste_capacite_lets_go.csv", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            type_id = type_map.get(normalize_key(row["type"]))
            category_id = category_map.get(normalize_key(row["classe"]))
            if not type_id or not category_id:
                raise ValueError(f"Missing type or category for move {row['nom_français']}")
            damage_type = row.get("type_degats") or None
            priority = get_priority_from_damage_type(damage_type)
            upsert_move(
                session,
                name=row["nom_français"].strip(),
                type_id=type_id,
                category_id=category_id,
                power=normalize_int(row.get("puissance")),
                accuracy=normalize_int(row.get("précision")),
                description=row.get("description"),
                damage_type=damage_type,
                priority=priority,
            )
    session.commit()
    print("✔ Moves inserted")


# ---------------------------------------------------------------------
# Load POKÉMON SPECIES
# ---------------------------------------------------------------------
def load_pokemon_species(session):
    """Load canonical Pokémon species reference data (independent of forms)."""
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
    """Load Pokémon forms and associate each Pokémon with a form. Assumes Forms table pre-initialized."""
    print("➡ Loading pokemon forms...")
    form_map = {f.name: f.id for f in session.query(Form).all()}

    with open(f"{DATA_PATH}/liste_pokemon.csv", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            species_id = int(row["id"])
            is_mega = normalize_bool(row.get("mega"))
            is_alola = normalize_bool(row.get("alola"))
            is_starter = normalize_bool(row.get("starter"))

            form_name = (
                "mega" if is_mega
                else "alola" if is_alola
                else "starter" if is_starter
                else "base"
            )
            form_id = form_map.get(form_name)
            if not form_id:
                raise ValueError(f"Form '{form_name}' not found in DB. Ensure init_db created it.")

            upsert_pokemon(
                session,
                species_id=species_id,
                form_id=form_id,
                name_pokeapi=row.get("nom_pokeapi"),
                name_pokepedia=row.get("nom_pokepedia"),
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
    """Associate Pokémon forms with elemental types (slot 1 and slot 2)."""
    print("➡ Loading pokemon types...")
    from core.models import Pokemon, Type

    type_map = {
        normalize_key(t.name): t.id
        for t in session.query(Type).all()
    }

    with open(f"{DATA_PATH}/liste_pokemon.csv", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            species_id = int(row["id"])

            form_name = (
                "mega" if normalize_bool(row.get("mega"))
                else "alola" if normalize_bool(row.get("alola"))
                else "starter" if normalize_bool(row.get("starter"))
                else "base"
            )

            pokemon = (
                session.query(Pokemon)
                .join(Form)
                .filter(Pokemon.species_id == species_id)
                .filter(Form.name == form_name)
                .one_or_none()
            )

            if not pokemon:
                continue

            # Slot 1
            if row.get("type_1"):
                type_id = type_map.get(normalize_key(row["type_1"]))
                if type_id:
                    upsert_pokemon_type(
                        session,
                        pokemon_id=pokemon.id,
                        type_id=type_id,
                        slot=1,
                    )

            # Slot 2
            if row.get("type_2"):
                type_id = type_map.get(normalize_key(row["type_2"]))
                if type_id:
                    upsert_pokemon_type(
                        session,
                        pokemon_id=pokemon.id,
                        type_id=type_id,
                        slot=2,
                    )

    session.commit()
    print("✔ Pokemon types inserted")


# ---------------------------------------------------------------------
# Load TYPE EFFECTIVENESS
# ---------------------------------------------------------------------
def load_type_effectiveness(session):
    """Load type effectiveness multipliers from table_type.csv."""
    print("➡ Loading type effectiveness...")
    from core.models import Type
    type_map = {normalize_key(t.name): t.id for t in session.query(Type).all()}

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
    """Execute the CSV ETL pipeline in the correct loading order."""
    session = SessionLocal()
    try:
        load_types(session)
        load_move_categories(session)
        load_moves(session)
        load_pokemon_species(session)
        load_pokemon(session)
        load_pokemon_types(session)
        load_type_effectiveness(session)
    finally:
        session.close()


if __name__ == "__main__":
    main()
