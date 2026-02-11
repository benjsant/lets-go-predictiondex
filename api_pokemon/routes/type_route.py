# api_pokemon/routes/type_route.py
"""API routes for Pokemon types and effectiveness."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api_pokemon.services.type_service import (
    get_type_affinities,
    get_type_affinities_by_name,
    list_pokemon_by_type,
    list_pokemon_by_type_name,
    list_types,
)
from core.db.session import get_db
from core.schemas.form import FormOut
from core.schemas.pokemon import PokemonListItem
from core.schemas.pokemon_type import PokemonTypeOut
from core.schemas.type import TypeOut
from core.schemas.type_effectiveness import TypeEffectivenessOut

router = APIRouter(prefix="/types", tags=["Types"])


# -------------------------------------------------------------------
# Types
# -------------------------------------------------------------------
@router.get("/", response_model=List[TypeOut])
def get_types(db: Session = Depends(get_db)):
    """List all 18 Pokemon types."""
    return list_types(db)


# -------------------------------------------------------------------
# Type effectiveness (IDs)
# -------------------------------------------------------------------
@router.get("/affinities", response_model=List[TypeEffectivenessOut])
def get_affinities(
    attacking_type_id: Optional[int] = Query(None, ge=1),
    defending_type_id: Optional[int] = Query(None, ge=1),
    db: Session = Depends(get_db),
):
    """Get type effectiveness by type IDs."""
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
# Type effectiveness (names)
# -------------------------------------------------------------------
@router.get("/affinities/by-name", response_model=List[TypeEffectivenessOut])
def get_affinities_by_name(
    attacking: Optional[str] = Query(None, min_length=1),
    defending: Optional[str] = Query(None, min_length=1),
    db: Session = Depends(get_db),
):
    """Get type effectiveness by type names."""
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
# Pokémon by type (name)
# Must be defined before /{type_id} route
# -------------------------------------------------------------------
@router.get("/by-name/{type_name}/pokemon", response_model=List[PokemonListItem])
def get_pokemon_by_type_name(
    type_name: str,
    db: Session = Depends(get_db),
):
    """List Pokemon of a specific type by name."""
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
# Pokémon by type (ID)
# -------------------------------------------------------------------
@router.get("/{type_id}/pokemon", response_model=List[PokemonListItem])
def get_pokemon_by_type(
    type_id: int,
    db: Session = Depends(get_db),
):
    """List Pokemon of a specific type by ID."""
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
