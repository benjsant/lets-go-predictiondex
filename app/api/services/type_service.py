# app/api/services/type_service.py
"""
Pokémon Type service layer
=========================

This module provides database access functions related to Pokémon types,
type effectiveness, and type-based Pokémon queries.

Responsibilities:
- Fetch elemental types
- Fetch type effectiveness (attack / defense affinities)
- Fetch Pokémon filtered by elemental type (slot 1 or 2)

This layer returns SQLAlchemy ORM objects and performs no serialization.
"""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.models import (
    Type,
    TypeEffectiveness,
    Pokemon,
    PokemonType,
)


# -------------------------
# 🔹 List all types
# -------------------------
def list_types(db: Session) -> List[Type]:
    """
    Retrieve all Pokémon elemental types.

    Returns
    -------
    List[Type]
        Ordered list of Type ORM objects.
    """
    return (
        db.query(Type)
        .order_by(Type.id)
        .all()
    )


# -------------------------
# 🔹 Type effectiveness (affinities)
# -------------------------
def get_type_affinities(
    db: Session,
    attacking_type_id: Optional[int] = None,
    defending_type_id: Optional[int] = None,
) -> List[TypeEffectiveness]:
    """
    Retrieve type effectiveness relationships.

    Can be filtered by:
    - attacking type ID
    - defending type ID
    - both (specific matchup)

    This function intentionally returns raw ORM objects
    to support both:
    - ML feature extraction
    - API-level enrichment in routes
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


# -------------------------
# 🔹 List Pokémon by type
# -------------------------
def list_pokemon_by_type(
    db: Session,
    type_id: int,
) -> List[Pokemon]:
    """
    List all Pokémon having a given elemental type
    in slot 1 or slot 2.

    Parameters
    ----------
    type_id : int
        ID of the elemental type.

    Returns
    -------
    List[Pokemon]
        Pokémon ORM objects with form, species and types loaded.
    """
    return (
        db.query(Pokemon)
        .join(PokemonType, PokemonType.pokemon_id == Pokemon.id)
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

def list_pokemon_by_type_name(db: Session, type_name: str) -> List[Pokemon]:
    """
    List all Pokémon having a type matching the given name.
    """
    return (
        db.query(Pokemon)
        .join(Pokemon.types).join(PokemonType.type)
        .filter(Type.name.ilike(type_name))
        .options(
            joinedload(Pokemon.form),
            joinedload(Pokemon.species),
            joinedload(Pokemon.types).joinedload(PokemonType.type),
        )
        .order_by(Pokemon.id)
        .all()
    )
