# app/db/guards/type.py

"""
Database guard for Pokémon types.

This module ensures that Pokémon types are uniquely stored
and reused during ETL processes.
"""

from sqlalchemy.orm import Session
from app.models import Type
from .utils import commit_if_needed


def upsert_type(
    session: Session,
    name: str,
    auto_commit: bool = False,
) -> Type:
    """
    Insert or retrieve a Pokémon type.

    Type names are compared case-insensitively to avoid duplicates.

    Args:
        session (Session): Active SQLAlchemy session.
        name (str): Type name (e.g. fire, water).
        auto_commit (bool): Whether to commit immediately.

    Returns:
        Type: Existing or newly created Type instance.
    """
    type_obj = session.query(Type).filter(
        Type.name.ilike(name)
    ).one_or_none()

    if type_obj:
        return type_obj

    type_obj = Type(name=name)
    session.add(type_obj)
    commit_if_needed(session, auto_commit)
    return type_obj
