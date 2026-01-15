#app\api\services\type_service.py
"""
Pokémon Type service layer
=========================

This module provides database access functions related to Pokémon elemental
types, type effectiveness (affinities), and Pokémon filtering by type.

Responsibilities:
- Fetch all elemental types
- Resolve a type by name (tolerant matching)
- Retrieve type effectiveness relationships
- Retrieve Pokémon by elemental type (ID or name)

This layer:
- Returns SQLAlchemy ORM objects only
- Contains no FastAPI / HTTP logic
- Is reusable for API, ML pipelines, and batch jobs
"""

import unicodedata
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.models import (
    Type,
    TypeEffectiveness,
    Pokemon,
    PokemonType,
)


# -------------------------------------------------------------------
# 🔹 Internal helpers
# -------------------------------------------------------------------
def normalize(text: str) -> str:
    """
    Normalize a string for tolerant comparison.

    Operations:
    - lowercase
    - remove accents (diacritics)

    Example:
    - "Ténèbres" → "tenebres"
    - "Fée" → "fee"
    """
    return "".join(
        c
        for c in unicodedata.normalize("NFD", text.lower())
        if unicodedata.category(c) != "Mn"
    )


def find_type_by_name(db: Session, name: str) -> Optional[Type]:
    """
    Resolve a Pokémon type using tolerant name matching.

    Matching rules:
    - accent-insensitive
    - case-insensitive
    - prefix-based (starts with)

    Examples:
    - "fee" → "Fée"
    - "teneb" → "Ténèbres"

    Returns
    -------
    Optional[Type]
        Matching Type ORM object, or None if not found.
    """
    normalized_input = normalize(name)

    for t in db.query(Type).all():
        if normalize(t.name).startswith(normalized_input):
            return t

    return None


# -------------------------------------------------------------------
# 🔹 Types
# -------------------------------------------------------------------
def list_types(db: Session) -> List[Type]:
    """
    Retrieve all Pokémon elemental types.

    Returns
    -------
    List[Type]
        Ordered list of all types.
    """
    return (
        db.query(Type)
        .order_by(Type.id)
        .all()
    )


# -------------------------------------------------------------------
# 🔹 Type effectiveness (affinities)
# -------------------------------------------------------------------
def get_type_affinities(
    db: Session,
    attacking_type_id: Optional[int] = None,
    defending_type_id: Optional[int] = None,
) -> List[TypeEffectiveness]:
    """
    Retrieve type effectiveness relationships.

    Parameters
    ----------
    attacking_type_id : Optional[int]
        Filter by attacking type ID.
    defending_type_id : Optional[int]
        Filter by defending type ID.

    Returns
    -------
    List[TypeEffectiveness]
        Matching effectiveness relationships.
    """
    query = db.query(TypeEffectiveness)

    if attacking_type_id is not None:
        query = query.filter(
            TypeEffectiveness.attacking_type_id == attacking_type_id
        )

    if defending_type_id is not None:
        query = query.filter(
            TypeEffectiveness.defending_type_id == defending_type_id
        )

    return query.all()


def get_type_affinities_by_name(
    db: Session,
    attacking_type_name: Optional[str] = None,
    defending_type_name: Optional[str] = None,
) -> List[TypeEffectiveness]:
    """
    Retrieve type effectiveness relationships using type names.

    Name matching is tolerant (accent- and case-insensitive).

    Parameters
    ----------
    attacking_type_name : Optional[str]
        Name of the attacking type.
    defending_type_name : Optional[str]
        Name of the defending type.

    Returns
    -------
    List[TypeEffectiveness]
        Matching effectiveness relationships.
    """
    attacking_type = (
        find_type_by_name(db, attacking_type_name)
        if attacking_type_name else None
    )
    defending_type = (
        find_type_by_name(db, defending_type_name)
        if defending_type_name else None
    )

    query = db.query(TypeEffectiveness)

    if attacking_type:
        query = query.filter(
            TypeEffectiveness.attacking_type_id == attacking_type.id
        )

    if defending_type:
        query = query.filter(
            TypeEffectiveness.defending_type_id == defending_type.id
        )

    return query.all()


# -------------------------------------------------------------------
# 🔹 Pokémon by type
# -------------------------------------------------------------------
def list_pokemon_by_type(
    db: Session,
    type_id: int,
) -> List[Pokemon]:
    """
    List all Pokémon having a given elemental type.

    The type can appear in slot 1 or slot 2.

    Parameters
    ----------
    type_id : int
        Elemental type ID.

    Returns
    -------
    List[Pokemon]
        Pokémon ORM objects with form, species and types loaded.
    """
    return (
        db.query(Pokemon)
        .join(PokemonType)
        .filter(PokemonType.type_id == type_id)
        .options(
            joinedload(Pokemon.form),
            joinedload(Pokemon.species),
            joinedload(Pokemon.types)
                .joinedload(PokemonType.type),
        )
        .order_by(Pokemon.id)
        .all()
    )


def list_pokemon_by_type_name(
    db: Session,
    type_name: str,
) -> List[Pokemon]:
    """
    List all Pokémon having a given elemental type, resolved by name.

    Parameters
    ----------
    type_name : str
        Elemental type name (tolerant matching).

    Returns
    -------
    List[Pokemon]
        Pokémon ORM objects.
    """
    type_obj = find_type_by_name(db, type_name)

    if not type_obj:
        return []

    return list_pokemon_by_type(db, type_obj.id)
