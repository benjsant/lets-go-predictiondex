"""
Move service layer
==================

Service functions for accessing and retrieving Pokémon move data.
Eager-loads related entities to prevent N+1 queries.
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

    Eager-loads:
    - Type
    - Move category

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
        .options(
            joinedload(Move.type),
            joinedload(Move.category)
        )
        .order_by(Move.id)
        .all()
    )


# -------------------------
# 🔹 Move detail
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
        .options(
            joinedload(Move.type),
            joinedload(Move.category)
        )
        .filter(Move.id == move_id)
        .one_or_none()
    )
