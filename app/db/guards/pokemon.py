# app/db/guards/pokemon.py

from sqlalchemy.orm import Session
from app.models import Pokemon
from .utils import commit_if_needed


def upsert_pokemon(
    session: Session,
    *,
    species_id: int,
    form_name: str,
    nom_pokeapi: str,
    nom_pokepedia: str,
    is_mega: bool = False,
    is_alola: bool = False,
    is_starter: bool = False,
    height_m=0,
    weight_kg=0,
    sprite_url=None,
    auto_commit: bool = False,
) -> Pokemon:
    pokemon = session.query(Pokemon).filter(
        Pokemon.species_id == species_id,
        Pokemon.form_name == form_name,
    ).one_or_none()

    if pokemon:
        return pokemon

    pokemon = Pokemon(
        species_id=species_id,
        form_name=form_name,
        nom_pokeapi=nom_pokeapi,
        nom_pokepedia=nom_pokepedia,
        is_mega=is_mega,
        is_alola=is_alola,
        is_starter=is_starter,
        height_m=height_m,
        weight_kg=weight_kg,
        sprite_url=sprite_url,
    )
    session.add(pokemon)
    commit_if_needed(session, auto_commit)
    return pokemon
