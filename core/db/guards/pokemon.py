# app/db/guards/pokemon.py
"""Safe upsert helpers for Pokemon records."""

from sqlalchemy.orm import Session

from core.models import Pokemon

from .utils import commit_if_needed


def upsert_pokemon(
    session: Session,
    *,
    species_id: int,
    form_id: int,
    name_pokeapi: str,
    name_pokepedia: str,
    height_m: float,
    weight_kg: float,
    sprite_url: str | None = None,
    auto_commit: bool = False,
) -> Pokemon:
    """Insert or retrieve a Pokemon form by species and form ID."""

    pokemon = (
        session.query(Pokemon)
        .filter(
            Pokemon.species_id == species_id,
            Pokemon.form_id == form_id,
        )
        .one_or_none()
    )

    if pokemon:
        return pokemon

    pokemon = Pokemon(
        species_id=species_id,
        form_id=form_id,
        name_pokeapi=name_pokeapi,
        name_pokepedia=name_pokepedia,
        height_m=height_m,
        weight_kg=weight_kg,
        sprite_url=sprite_url,
    )

    session.add(pokemon)
    commit_if_needed(session, auto_commit)
    return pokemon
