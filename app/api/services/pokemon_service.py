"""
Pokémon service layer
====================

This module provides database access functions related to Pokémon entities.

It is responsible for retrieving Pokémon data using SQLAlchemy ORM and
eager-loading all required relationships (species, stats, types, moves,
learn methods) to ensure optimal performance and avoid N+1 query issues.

The service layer returns SQLAlchemy model instances and does not perform
any serialization or API-specific logic.
"""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.models import (
    Pokemon,
    PokemonMove,
    Move,
    PokemonType,
)


# -------------------------
# 🔹 List Pokémon
# -------------------------
def list_pokemon(db: Session) -> List[Pokemon]:
    """
    Retrieve all Pokémon from the database.

    This function returns all Pokémon ordered by their internal identifier.
    The following related entities are eagerly loaded:
    - Pokémon species
    - Pokémon types and their associated type details

    Parameters
    ----------
    db : Session
        Active SQLAlchemy database session.

    Returns
    -------
    List[Pokemon]
        List of SQLAlchemy Pokémon objects.
    """
    return (
        db.query(Pokemon)
        .options(
            joinedload(Pokemon.species),
            joinedload(Pokemon.types).joinedload(PokemonType.type),
        )
        .order_by(Pokemon.id)
        .all()
    )


# -------------------------
# 🔹 Pokémon detail
# -------------------------
def get_pokemon_by_id(
    db: Session,
    pokemon_id: int,
) -> Optional[Pokemon]:
    """
    Retrieve a Pokémon by its unique identifier.

    This function eagerly loads all related entities required for a detailed
    Pokémon view, including:
    - Species information
    - Base statistics
    - Types and type details
    - Moves learned by the Pokémon
    - Move details and move types
    - Learning methods associated with each move

    Parameters
    ----------
    db : Session
        Active SQLAlchemy database session.
    pokemon_id : int
        Unique identifier of the Pokémon.

    Returns
    -------
    Optional[Pokemon]
        The corresponding Pokémon object if found, otherwise ``None``.
    """
    return (
        db.query(Pokemon)
        .options(
            joinedload(Pokemon.species),
            joinedload(Pokemon.stats),
            joinedload(Pokemon.types).joinedload(PokemonType.type),
            joinedload(Pokemon.moves)
                .joinedload(PokemonMove.move)
                .joinedload(Move.type),
            joinedload(Pokemon.moves)
                .joinedload(PokemonMove.learn_method),
        )
        .filter(Pokemon.id == pokemon_id)
        .one_or_none()
    )
