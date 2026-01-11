"""
API routes – Pokémon
===================

This module defines the FastAPI routes related to Pokémon entities.

It provides read-only endpoints to:
- list all Pokémon with basic information,
- retrieve detailed data for a specific Pokémon, including stats, types, and moves.

The routes rely on a dedicated service layer (`pokemon_service`) to access
the database and encapsulate business logic.
"""
## pylint: disable=import-error
from typing import List
from fastapi import APIRouter, HTTPException

from app.db.session import SessionLocal
from app.schemas.pokemon import (
    PokemonListItem,
    PokemonDetail,
    PokemonMoveOut,
)
from app.schemas.pokemon_type import PokemonTypeOut
from app.api.services.pokemon_service import (
    list_pokemon,
    get_pokemon_by_id,
)

router = APIRouter()


# -------------------------
# 🔹 Pokémon list
# -------------------------
@router.get("/", response_model=List[PokemonListItem])
def get_pokemon_list():
    """
    Retrieve the list of all Pokémon.

    Returns a summarized representation for each Pokémon, including:
    - form and variant flags (Mega, Alola, starter),
    - species information,
    - primary and secondary types,
    - sprite URL when available.

    This endpoint is designed for:
    - Pokédex-style listings,
    - frontend overviews,
    - analytical or exploratory use cases.
    """
    with SessionLocal() as db:
        pokemons = list_pokemon(db)

        return [
            PokemonListItem(
                id=p.id,
                form_name=p.form_name,
                is_mega=p.is_mega,
                is_alola=p.is_alola,
                is_starter=p.is_starter,
                species=p.species,
                sprite_url=p.sprite_url,
                types=[
                    PokemonTypeOut(
                        slot=pt.slot,
                        name=pt.type.name,
                    )
                    for pt in p.types
                ],
            )
            for p in pokemons
        ]


# -------------------------
# 🔹 Pokémon detail
# -------------------------
@router.get("/{pokemon_id}", response_model=PokemonDetail)
def get_pokemon_detail(pokemon_id: int):
    """
    Retrieve detailed information about a specific Pokémon.

    Parameters
    ----------
    pokemon_id : int
        Unique identifier of the Pokémon.

    Returns
    -------
    PokemonDetail
        A detailed Pokémon representation including:
        - base information and form flags,
        - species data,
        - base stats,
        - physical characteristics (height, weight),
        - types,
        - learnable moves with learning conditions.

    Raises
    ------
    HTTPException
        404 error if the Pokémon does not exist.
    """
    with SessionLocal() as db:
        pokemon = get_pokemon_by_id(db, pokemon_id)

        if not pokemon:
            raise HTTPException(
                status_code=404,
                detail="Pokemon not found",
            )

        return PokemonDetail(
            id=pokemon.id,
            form_name=pokemon.form_name,
            is_mega=pokemon.is_mega,
            is_alola=pokemon.is_alola,
            is_starter=pokemon.is_starter,
            species=pokemon.species,
            stats=pokemon.stats,
            height_m=pokemon.height_m,
            weight_kg=pokemon.weight_kg,
            sprite_url=pokemon.sprite_url,
            types=[
                PokemonTypeOut(
                    slot=pt.slot,
                    name=pt.type.name,
                )
                for pt in pokemon.types
            ],
            moves=[
                PokemonMoveOut(
                    name=pm.move.name,
                    type=pm.move.type.name,
                    learn_method=pm.learn_method.name,
                    learn_level=pm.learn_level,
                )
                for pm in pokemon.moves
            ],
        )
