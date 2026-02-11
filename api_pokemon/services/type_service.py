# api_pokemon/services/type_service.py
"""Database access functions for Pokemon types and effectiveness."""

import unicodedata
from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from core.models import (
    Pokemon,
    PokemonType,
    Type,
    TypeEffectiveness,
)


# -------------------------------------------------------------------
# Internal helpers
# -------------------------------------------------------------------
def normalize(text: str) -> str:
    """Normalize string for comparison (lowercase, remove accents)."""
    return "".join(
        c
        for c in unicodedata.normalize("NFD", text.lower())
        if unicodedata.category(c) != "Mn"
    )


def find_type_by_name(db: Session, name: str) -> Optional[Type]:
    """Find a type by name (accent and case insensitive, prefix match)."""
    normalized_input = normalize(name)

    for t in db.query(Type).all():
        if normalize(t.name).startswith(normalized_input):
            return t

    return None


# -------------------------------------------------------------------
# Types
# -------------------------------------------------------------------
def list_types(db: Session) -> List[Type]:
    """Retrieve all Pokemon elemental types."""
    return (
        db.query(Type)
        .order_by(Type.id)
        .all()
    )


# -------------------------------------------------------------------
# Type effectiveness (affinities)
# -------------------------------------------------------------------
def get_type_affinities(
    db: Session,
    attacking_type_id: Optional[int] = None,
    defending_type_id: Optional[int] = None,
) -> List[TypeEffectiveness]:
    """Retrieve type effectiveness relationships, optionally filtered."""
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
    """Retrieve type effectiveness by type names (tolerant matching)."""
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
# Pokémon by type
# -------------------------------------------------------------------
def list_pokemon_by_type(
    db: Session,
    type_id: int,
) -> List[Pokemon]:
    """List Pokemon having a given elemental type."""
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
    """List Pokemon having a given type by name."""
    type_obj = find_type_by_name(db, type_name)

    if not type_obj:
        return []

    return list_pokemon_by_type(db, type_obj.id)
