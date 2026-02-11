# app/db/guards/move.py
"""Safe upsert helpers for Pokemon move records."""

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
    """Insert or retrieve a Pokemon move by name."""
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
