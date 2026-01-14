"""
Move service layer
==================

Service functions for accessing and retrieving Pokémon move data.
Eager-loads related entities to prevent N+1 queries.

New features:
- Filter moves by type name
- Optional filtering by Pokémon ID
"""

import unicodedata
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models import Move, PokemonMove, Pokemon, Type


# -------------------------
# 🔹 Utility function
# -------------------------
def normalize(text: str) -> str:
    """
    Normalize a string for tolerant comparison:
    - lowercase
    - remove accents
    """
    return "".join(
        c for c in unicodedata.normalize("NFD", text.lower())
        if unicodedata.category(c) != "Mn"
    )


# -------------------------
# 🔹 List all moves
# -------------------------
def list_moves(db: Session) -> List[Move]:
    """
    Retrieve all moves from the database, eager-loading type and category.

    Parameters
    ----------
    db : Session
        Active SQLAlchemy session.

    Returns
    -------
    List[Move]
        List of Move ORM objects.
    """
    return (
        db.query(Move)
        .options(joinedload(Move.type), joinedload(Move.category))
        .order_by(Move.id)
        .all()
    )


# -------------------------
# 🔹 Retrieve move by ID
# -------------------------
def get_move_by_id(db: Session, move_id: int) -> Optional[Move]:
    """
    Retrieve a move by its unique ID, eager-loading type and category.

    Parameters
    ----------
    db : Session
        Active SQLAlchemy session.
    move_id : int
        Move ID.

    Returns
    -------
    Optional[Move]
        Move ORM object if found, else None.
    """
    return (
        db.query(Move)
        .options(joinedload(Move.type), joinedload(Move.category))
        .filter(Move.id == move_id)
        .one_or_none()
    )


# -------------------------
# 🔹 Search moves by name (French)
# -------------------------
def search_moves_by_name(db: Session, name: str) -> List[Move]:
    """
    Search moves by name in French (partial match, accent-insensitive).

    Parameters
    ----------
    db : Session
        Active SQLAlchemy session.
    name : str
        Partial or full name to search.

    Returns
    -------
    List[Move]
        List of matching Move ORM objects.
    """
    normalized_name = normalize(name)

    moves = db.query(Move).options(joinedload(Move.type), joinedload(Move.category)).all()
    return [m for m in moves if normalize(m.name).find(normalized_name) != -1]


# -------------------------
# 🔹 List moves by type
# -------------------------
def list_moves_by_type(
    db: Session,
    type_name: str,
    pokemon_id: Optional[int] = None
):
    """
    List moves by type.
    Optionally include Pokémon-specific learning info.
    """
    type_obj = next(
        (t for t in db.query(Type).all()
         if normalize(t.name).startswith(normalize(type_name))),
        None
    )
    if not type_obj:
        return []

    if pokemon_id:
        return (
            db.query(Move, PokemonMove)
            .join(PokemonMove)
            .filter(
                Move.type_id == type_obj.id,
                PokemonMove.pokemon_id == pokemon_id,
            )
            .options(
                joinedload(Move.type),
                joinedload(Move.category),
                joinedload(PokemonMove.learn_method),
            )
            .order_by(Move.id)
            .all()
        )

    return (
        db.query(Move)
        .options(joinedload(Move.type), joinedload(Move.category))
        .filter(Move.type_id == type_obj.id)
        .order_by(Move.id)
        .all()
    )

