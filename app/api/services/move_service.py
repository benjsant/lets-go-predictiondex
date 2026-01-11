"""
Move service layer
==================

This module contains the service functions responsible for accessing and
retrieving move (attack) data from the database.

The service layer isolates database logic from API routes and returns
SQLAlchemy model instances, optionally eager-loading related entities
to avoid N+1 query issues.
"""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.models import Move


# -------------------------
# 🔹 List moves
# -------------------------
def list_moves(db: Session) -> List[Move]:
    """
    Retrieve all moves from the database.

    This function returns all move entities and eagerly loads the related
    Pokémon type to optimize database access and prevent N+1 queries.

    Parameters
    ----------
    db : Session
        Active SQLAlchemy database session.

    Returns
    -------
    List[Move]
        List of SQLAlchemy Move objects.
    """
    return (
        db.query(Move)
        .options(joinedload(Move.type))
        .all()
    )


# -------------------------
# 🔹 Move detail
# -------------------------
def get_move_by_id(db: Session, move_id: int) -> Optional[Move]:
    """
    Retrieve a move by its unique identifier.

    The related move type is eagerly loaded to provide complete information
    in a single database query.

    Parameters
    ----------
    db : Session
        Active SQLAlchemy database session.
    move_id : int
        Unique identifier of the move.

    Returns
    -------
    Optional[Move]
        The corresponding Move object if found, otherwise ``None``.
    """
    return (
        db.query(Move)
        .options(joinedload(Move.type))
        .filter(Move.id == move_id)
        .one_or_none()
    )
