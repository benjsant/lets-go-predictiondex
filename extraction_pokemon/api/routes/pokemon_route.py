# extraction_pokemon/api/routes/pokemon_route.py

from typing import List
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session

from extraction_pokemon.db.session import get_db
from extraction_pokemon.api.services.pokemon_service import (
    list_pokemon,
    get_pokemon_by_id,
    search_pokemon_by_species_name,
)

from extraction_pokemon.schemas.pokemon import (
    PokemonListItem,
    PokemonDetail,
    PokemonMoveUIOut,
)
from extraction_pokemon.schemas.pokemon_type import PokemonTypeOut
from extraction_pokemon.schemas.form import FormOut
from extraction_pokemon.schemas.pokemon_weakness import PokemonWeaknessOut
from extraction_pokemon.api.services.pokemon_service import compute_pokemon_weaknesses

router = APIRouter(prefix="/pokemon", tags=["Pokemon"])


# ============================================================
# 🔹 Pokémon list
# ============================================================
@router.get("/", response_model=List[PokemonListItem])
def get_pokemon_list(db: Session = Depends(get_db)):
    pokemons = list_pokemon(db)

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


# ============================================================
# 🔹 Search Pokémon by species name
# ⚠️ DOIT être avant /{pokemon_id}
# ============================================================
@router.get("/search", response_model=List[PokemonListItem])
def search_pokemon(
    name: str = Query(..., min_length=1),
    lang: str = Query("fr", pattern="^(fr|en|jp)$"),
    db: Session = Depends(get_db),
):
    """
    Search Pokémon by species name (partial match).

    Streamlit-friendly:
    - returns [] if no match
    """
    pokemons = search_pokemon_by_species_name(db, name=name, lang=lang)

    # 🔧 PAS de 404 ici
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


# ============================================================
# 🔹 Pokémon detail
# ============================================================
@router.get("/{pokemon_id}", response_model=PokemonDetail)
def get_pokemon_detail(
    pokemon_id: int,
    db: Session = Depends(get_db),
):
    pokemon = get_pokemon_by_id(db, pokemon_id)

    if not pokemon:
        raise HTTPException(
            status_code=404,
            detail="Pokemon not found",
        )

    return PokemonDetail(
        id=pokemon.id,
        form=FormOut(
            id=pokemon.form.id,
            name=pokemon.form.name,
        ),
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
            PokemonMoveUIOut(
                name=pm.move.name,
                type=pm.move.type.name,
                category=pm.move.category.name,
                learn_method=pm.learn_method.name,
                learn_level=pm.learn_level,
                power=pm.move.power,
                accuracy=pm.move.accuracy,
                damage_type=pm.move.damage_type if pm.move.damage_type else None,
            )
            for pm in pokemon.moves
        ],
    )

@router.get(
    "/{pokemon_id}/weaknesses",
    response_model=list[PokemonWeaknessOut],
)
def get_pokemon_weaknesses(
    pokemon_id: int,
    db: Session = Depends(get_db),
):
    weaknesses = compute_pokemon_weaknesses(db, pokemon_id)

    if weaknesses is None:
        raise HTTPException(
            status_code=404,
            detail="Pokemon not found",
        )

    return weaknesses
