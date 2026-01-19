# extraction_pokemon/api/routes/type_route.py
"""
API routes – Pokémon types
=========================

This module exposes REST endpoints related to Pokémon elemental types.

Routes include:
- Type listing
- Type effectiveness (by ID or by name)
- Pokémon filtering by type (ID or name)

This layer:
- Handles HTTP concerns only
- Delegates all data access to the service layer
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session

from extraction_pokemon.db.session import get_db
from extraction_pokemon.api.services.type_service import (
    list_types,
    get_type_affinities,
    get_type_affinities_by_name,
    list_pokemon_by_type,
    list_pokemon_by_type_name,
)

from extraction_pokemon.schemas.type import TypeOut
from extraction_pokemon.schemas.type_effectiveness import TypeEffectivenessOut
from extraction_pokemon.schemas.pokemon import PokemonListItem
from extraction_pokemon.schemas.pokemon_type import PokemonTypeOut
from extraction_pokemon.schemas.form import FormOut

router = APIRouter(prefix="/types", tags=["Types"])


# -------------------------------------------------------------------
# 🔹 Types
# -------------------------------------------------------------------
@router.get("/", response_model=List[TypeOut])
def get_types(db: Session = Depends(get_db)):
    """List all Pokémon elemental types."""
    return list_types(db)


# -------------------------------------------------------------------
# 🔹 Type effectiveness (IDs)
# -------------------------------------------------------------------
@router.get("/affinities", response_model=List[TypeEffectivenessOut])
def get_affinities(
    attacking_type_id: Optional[int] = Query(None, ge=1),
    defending_type_id: Optional[int] = Query(None, ge=1),
    db: Session = Depends(get_db),
):
    affinities = get_type_affinities(
        db,
        attacking_type_id=attacking_type_id,
        defending_type_id=defending_type_id,
    )

    if not affinities:
        raise HTTPException(
            status_code=404,
            detail="No type effectiveness found for given parameters",
        )

    return affinities


# -------------------------------------------------------------------
# 🔹 Type effectiveness (names)
# -------------------------------------------------------------------
@router.get("/affinities/by-name", response_model=List[TypeEffectivenessOut])
def get_affinities_by_name(
    attacking: Optional[str] = Query(None, min_length=1),
    defending: Optional[str] = Query(None, min_length=1),
    db: Session = Depends(get_db),
):
    affinities = get_type_affinities_by_name(
        db,
        attacking_type_name=attacking,
        defending_type_name=defending,
    )

    if not affinities:
        raise HTTPException(
            status_code=404,
            detail="No type effectiveness found for given parameters",
        )

    return affinities


# -------------------------------------------------------------------
# 🔹 Pokémon by type (name)
# ⚠️ AVANT /{type_id}
# -------------------------------------------------------------------
@router.get("/by-name/{type_name}/pokemon", response_model=List[PokemonListItem])
def get_pokemon_by_type_name(
    type_name: str,
    db: Session = Depends(get_db),
):
    pokemons = list_pokemon_by_type_name(db, type_name)

    if not pokemons:
        raise HTTPException(
            status_code=404,
            detail="No Pokémon found for this type name",
        )

    return [
        PokemonListItem(
            id=p.id,
            form=FormOut(id=p.form.id, name=p.form.name),
            species=p.species,
            sprite_url=p.sprite_url,
            types=[
                PokemonTypeOut(slot=pt.slot, name=pt.type.name)
                for pt in p.types
            ],
        )
        for p in pokemons
    ]


# -------------------------------------------------------------------
# 🔹 Pokémon by type (ID)
# -------------------------------------------------------------------
@router.get("/{type_id}/pokemon", response_model=List[PokemonListItem])
def get_pokemon_by_type(
    type_id: int,
    db: Session = Depends(get_db),
):
    pokemons = list_pokemon_by_type(db, type_id)

    if not pokemons:
        raise HTTPException(
            status_code=404,
            detail="No Pokémon found for this type",
        )

    return [
        PokemonListItem(
            id=p.id,
            form=FormOut(id=p.form.id, name=p.form.name),
            species=p.species,
            sprite_url=p.sprite_url,
            types=[
                PokemonTypeOut(slot=pt.slot, name=pt.type.name)
                for pt in p.types
            ],
        )
        for p in pokemons
    ]
