# app/db/guards/move.py

from sqlalchemy.orm import Session
from app.models import Move
from .utils import commit_if_needed


def upsert_move(
    session: Session,
    *,
    name: str,
    type_id: int,
    category: str,
    power=None,
    accuracy=None,
    description=None,
    damage_type=None,
    auto_commit: bool = False,
) -> Move:
    move = session.query(Move).filter(
        Move.name.ilike(name)
    ).one_or_none()

    if move:
        return move

    move = Move(
        name=name,
        type_id=type_id,
        category=category,
        power=power,
        accuracy=accuracy,
        description=description,
        damage_type=damage_type,
    )
    session.add(move)
    commit_if_needed(session, auto_commit)
    return move
