# app/db/guards/pokemon_move.py

"""
Database guard for Pokémon ↔ Move relationships.

This module handles safe insertion of Pokémon moves, ensuring
that duplicate associations are not created during ETL processes.
"""

from sqlalchemy.orm import Session
from app.models import PokemonMove
from .utils import commit_if_needed


def upsert_pokemon_move(
    session: Session,
    *,
    pokemon_id: int,
    move_id: int,
    learn_method_id: int,
    learn_level=None,
    auto_commit: bool = False,
) -> tuple[PokemonMove, bool]:
    """
    Insert or retrieve a Pokémon move association.

    A Pokémon can only learn a given move once per learning method
    and learning level.

    Args:
        session (Session): Active SQLAlchemy session.
        pokemon_id (int): Pokémon identifier.
        move_id (int): Move identifier.
        learn_method_id (int): Learning method identifier.
        learn_level (int | None): Level at which the move is learned.
        auto_commit (bool): Whether to commit immediately.

    Returns:
        tuple[PokemonMove, bool]:
            - PokemonMove: The association record.
            - bool: True if created, False if already existing.
    """
    pm = (
        session.query(PokemonMove)
        .filter(
            PokemonMove.pokemon_id == pokemon_id,
            PokemonMove.move_id == move_id,
            PokemonMove.learn_method_id == learn_method_id,
            PokemonMove.learn_level == learn_level,
        )
        .one_or_none()
    )

    if pm:
        return pm, False

    pm = PokemonMove(
        pokemon_id=pokemon_id,
        move_id=move_id,
        learn_method_id=learn_method_id,
        learn_level=learn_level,
    )

    session.add(pm)
    commit_if_needed(session, auto_commit)

    return pm, True
