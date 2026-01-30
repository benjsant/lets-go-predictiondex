"""
ETL – CSV Data Loading into Relational Database (Pokémon Let's Go).

This script implements the core deterministic ETL pipeline of the project.
It loads structured CSV reference data into the relational database and
establishes the foundational dataset used by all downstream processes.

Overview
--------
- Extracts structured data from CSV files
- Normalizes raw values (booleans, integers, string keys)
- Applies business rules (Pokémon forms, type slots, move priority)
- Loads data using idempotent upsert guards
- Ensures referential integrity between relational entities

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
- data normalization and transformation
- relational data modeling
- controlled loading into a SQL database
"""

from __future__ import annotations

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
from etl_pokemon.utils.constants import get_priority_from_damage_type
from etl_pokemon.utils.normalizers import normalize_bool, normalize_int, normalize_key

DATA_PATH = "etl_pokemon/data/csv"

# ---------------------------------------------------------------------
# Load TYPES
# ---------------------------------------------------------------------
def load_types(session) -> None:
    """
    Load Pokémon elemental types from liste_pokemon.csv.

    Types are deduplicated using normalized keys.
    """
    print("➡ Loading types...")
    seen: set[str] = set()

    with open(f"{DATA_PATH}/liste_pokemon.csv", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            for column in ("type_1", "type_2"):
                name = row.get(column)
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
def load_move_categories(session) -> None:
    """
    Verify that all move categories referenced in the CSV
    already exist in the database.

    Categories are assumed to be created during database initialization.
    """
    print("➡ Loading move categories...")
    seen: set[str] = set()

    with open(f"{DATA_PATH}/liste_capacite_lets_go.csv", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            name = row.get("classe")
            if not name:
                continue

            key = normalize_key(name)
            if key in seen:
                continue

            category = (
                session.query(MoveCategory)
                .filter_by(name=name.strip())
                .first()
            )

            if not category:
                raise ValueError(
                    f"MoveCategory '{name.strip()}' not found. "
                    "Ensure init_db created it."
                )

            seen.add(key)

    print(f"✔ {len(seen)} move categories verified")


# ---------------------------------------------------------------------
# Load MOVES
# ---------------------------------------------------------------------
def load_moves(session) -> None:
    """
    Load Pokémon moves with type, category, power, accuracy,
    damage behavior and computed priority.
    """
    print("➡ Loading moves...")
    from core.models import Type  # pylint: disable=import-outside-toplevel

    type_map = {
        normalize_key(t.name): t.id
        for t in session.query(Type).all()
    }
    category_map = {
        normalize_key(c.name): c.id
        for c in session.query(MoveCategory).all()
    }

    with open(f"{DATA_PATH}/liste_capacite_lets_go.csv", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            type_id = type_map.get(normalize_key(row["type"]))
            category_id = category_map.get(normalize_key(row["classe"]))

            if not type_id or not category_id:
                raise ValueError(
                    f"Missing type or category for move '{row['nom_français']}'"
                )

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
def load_pokemon_species(session) -> None:
    """
    Load canonical Pokémon species reference data.

    Species are independent from forms (base, mega, alola, starter).
    """
    print("➡ Loading Pokémon species...")

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
    print("✔ Pokémon species inserted")


# ---------------------------------------------------------------------
# Load POKÉMON FORMS
# ---------------------------------------------------------------------
def load_pokemon(session) -> None:
    """
    Load Pokémon forms and associate them with species.

    Assumes the Form table is already initialized.
    """
    print("➡ Loading Pokémon forms...")
    form_map = {form.name: form.id for form in session.query(Form).all()}

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

            form_id = form_map.get(form_name)
            if not form_id:
                raise ValueError(
                    f"Form '{form_name}' not found. Ensure init_db created it."
                )

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
    print("✔ Pokémon forms inserted")


# ---------------------------------------------------------------------
# Load POKÉMON ↔ TYPES
# ---------------------------------------------------------------------
def load_pokemon_types(session) -> None:
    """
    Associate Pokémon forms with their elemental types.

    Supports up to two type slots per Pokémon.
    """
    print("➡ Loading Pokémon types...")
    from core.models import Pokemon, Type  # pylint: disable=import-outside-toplevel

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

            if row.get("type_1"):
                upsert_pokemon_type(
                    session,
                    pokemon_id=pokemon.id,
                    type_id=type_map[normalize_key(row["type_1"])],
                    slot=1,
                )

            if row.get("type_2"):
                upsert_pokemon_type(
                    session,
                    pokemon_id=pokemon.id,
                    type_id=type_map[normalize_key(row["type_2"])],
                    slot=2,
                )

    session.commit()
    print("✔ Pokémon types inserted")


# ---------------------------------------------------------------------
# Load TYPE EFFECTIVENESS
# ---------------------------------------------------------------------
def load_type_effectiveness(session) -> None:
    """
    Load type effectiveness multipliers from table_type.csv.
    """
    print("➡ Loading type effectiveness...")
    from core.models import Type  # pylint: disable=import-outside-toplevel

    type_map = {
        normalize_key(t.name): t.id
        for t in session.query(Type).all()
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
def main() -> None:
    """
    Execute the CSV ETL pipeline in the correct loading order.
    """
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
