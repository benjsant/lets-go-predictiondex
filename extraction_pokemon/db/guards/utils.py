# app/db/guards/utils.py

"""
Shared utilities for database guards.

This module contains small helper functions used across guard
implementations to simplify session handling and error tolerance.
"""

from sqlalchemy.orm import Session


def get_one_or_none(query):
    """
    Safely execute a SQLAlchemy one_or_none query.

    Any unexpected exception is caught and results in None,
    preventing ETL failures due to transient or malformed queries.

    Args:
        query: SQLAlchemy query object.

    Returns:
        Any | None: Query result or None if not found or failed.
    """
    try:
        return query.one_or_none()
    except Exception:
        return None


def commit_if_needed(session: Session, auto_commit: bool):
    """
    Commit the current transaction if auto_commit is enabled.

    Args:
        session (Session): Active SQLAlchemy session.
        auto_commit (bool): Whether to commit immediately.
    """
    if auto_commit:
        session.commit()
