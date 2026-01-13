# app/api/routes/type_route.py
"""
API routes – Pokémon types
=========================
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from app.db.session import SessionLocal
from app.api.services.type_service import (
    list_types,
    get_type_affinities,
    list_pokemon_by_type,
)

from app.schemas.type import TypeOut
from app.schemas.type_effectiveness import TypeEffectivenessOut
from app.schemas.pokemon import PokemonListItem
from app.schemas.pokemon_type import PokemonTypeOut
from app.schemas.form import FormOut

router = APIRouter(prefix="/types", tags=["Types"])


# -------------------------
# 🔹 List all types
# -------------------------
@router.get("/", response_model=List[TypeOut])
def get_types():
    with SessionLocal() as db:
        return list_types(db)


# -------------------------
# 🔹 Type effectiveness
# -------------------------
@router.get("/affinities", response_model=List[TypeEffectivenessOut])
def get_affinities(
    attacking_type_id: Optional[int] = Query(None, ge=1),
    defending_type_id: Optional[int] = Query(None, ge=1),
):
    with SessionLocal() as db:
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


# -------------------------
# 🔹 Pokémon by type
# -------------------------
@router.get("/{type_id}/pokemon", response_model=List[PokemonListItem])
def get_pokemon_by_type(type_id: int):
    with SessionLocal() as db:
        pokemons = list_pokemon_by_type(db, type_id)

        if not pokemons:
            raise HTTPException(
                status_code=404,
                detail="No Pokémon found for this type",
            )

        return [
            PokemonListItem(
                id=p.id,
                form=FormOut(
                    id=p.form.id,
                    name=p.form.name,
                ),
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
