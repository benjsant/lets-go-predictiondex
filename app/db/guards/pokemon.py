# app/db/guards/pokemon.py

"""
Database guard for Pokémon forms.

This module provides safe upsert helpers for Pokémon records,
handling multiple forms (base, Mega, Alola, starter, etc.)
without duplicating entries.
"""

from sqlalchemy.orm import Session
from app.models import Pokemon
from .utils import commit_if_needed


def upsert_pokemon(
    session: Session,
    *,
    species_id: int,
    form_name: str,
    name_pokeapi: str,
    name_pokepedia: str,
    is_mega: bool = False,
    is_alola: bool = False,
    is_starter: bool = False,
    height_m=0,
    weight_kg=0,
    sprite_url=None,
    auto_commit: bool = False,
) -> Pokemon:
    """
    Insert or retrieve a Pokémon form.

    Pokémon are uniquely identified by their species and form name.
    If the Pokémon already exists, it is returned unchanged.

    Args:
        session (Session): Active SQLAlchemy session.
        species_id (int): Pokémon species identifier.
        form_name (str): Form name (Base, Mega X, Alola, etc.).
        name_pokeapi (str): Technical name from PokeAPI.
        name_pokepedia (str): Name as displayed on Poképédia.
        is_mega (bool): Whether this is a Mega evolution.
        is_alola (bool): Whether this is an Alolan form.
        is_starter (bool): Whether this Pokémon is starter-exclusive.
        height_m (float): Height in meters.
        weight_kg (float): Weight in kilograms.
        sprite_url (str | None): URL to sprite image.
        auto_commit (bool): Whether to commit immediately.

    Returns:
        Pokemon: Existing or newly created Pokémon instance.
    """
    pokemon = session.query(Pokemon).filter(
        Pokemon.species_id == species_id,
        Pokemon.form_name == form_name,
    ).one_or_none()

    if pokemon:
        return pokemon

    pokemon = Pokemon(
        species_id=species_id,
        form_name=form_name,
        name_pokeapi=name_pokeapi,
        name_pokepedia=name_pokepedia,
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
