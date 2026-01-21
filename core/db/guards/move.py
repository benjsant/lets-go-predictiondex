# app/db/guards/move.py

"""
Database guard for Pokémon moves.

This module provides helper functions used during ETL and data ingestion
to safely insert or retrieve Move records while preserving database
integrity and avoiding duplicates.
"""

from sqlalchemy.orm import Session
from core.models import Move
from .utils import commit_if_needed


def upsert_move(
    session: Session,
    *,
    name: str,
    type_id: int,
    category_id: int,
    power: int | None = None,
    accuracy: int | None = None,
    description: str | None = None,
    damage_type: str | None = None,
    priority: int = 0,
    auto_commit: bool = False,
) -> Move:
    """
    Insert or retrieve a Pokémon move.

    If a move with the same name already exists (case-insensitive),
    it is returned as-is. Otherwise, a new Move record is created.

    Args:
        session (Session): Active SQLAlchemy session.
        name (str): Move name.
        type_id (int): Foreign key to the Pokémon type.
        category (str): Move category (physical, special, status).
        power (int | None): Base power of the move.
        accuracy (int | None): Accuracy percentage.
        description (str | None): Move description.
        damage_type (str | None): Damage behavior (if applicable).
        priority (int): Move priority (-7 to +2, default 0).
        auto_commit (bool): Whether to commit immediately.

    Returns:
        Move: Existing or newly created Move instance.
    """
    move = (
        session.query(Move)
        .filter(Move.name.ilike(name))
        .one_or_none()
    )

    if move:
        # Update priority if it changed (allows re-running ETL)
        if move.priority != priority:
            move.priority = priority
            commit_if_needed(session, auto_commit)
        return move

    move = Move(
        name=name,
        type_id=type_id,
        category_id=category_id,
        power=power,
        accuracy=accuracy,
        description=description,
        damage_type=damage_type,
        priority=priority,
    )

    session.add(move)
    commit_if_needed(session, auto_commit)
    return move
