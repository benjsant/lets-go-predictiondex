# app/db/guards/pokemon_move.py

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
    Upsert d'une capacité Pokémon.

    Retourne:
        (PokemonMove, created)
        created = True si la ligne a été créée, False si elle existait déjà
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
