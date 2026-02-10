"""
Pokémon API Routes
==================

REST endpoints for querying Pokémon data from the database.

This module provides comprehensive Pokémon information including:
- Complete Pokémon listing with pagination and filters
- Detailed Pokémon data (stats, types, abilities, moves)
- Type effectiveness analysis (weaknesses/resistances)
- Species-based search functionality

Endpoints:
    GET /pokemon/ - List all Pokémon with optional filters
    GET /pokemon/{pokemon_id} - Get detailed Pokémon information
    GET /pokemon/species/{species_name} - Search by species name

All endpoints require API key authentication (if API_KEY_REQUIRED=true).

Example:
    ```python
    # Get all Pokémon
    GET /pokemon/

    # Get Pikachu details
    GET /pokemon/25

    # Search for Charizard
    GET /pokemon/species/Charizard
    ```
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api_pokemon.services.pokemon_service import (
    compute_pokemon_weaknesses,
    get_pokemon_by_id,
    list_pokemon,
    search_pokemon_by_species_name,
)
from core.db.session import get_db
from core.schemas.form import FormOut
from core.schemas.pokemon import (
    PokemonDetail,
    PokemonListItem,
    PokemonMoveUIOut,
)
from core.schemas.pokemon_type import PokemonTypeOut
from core.schemas.pokemon_weakness import PokemonWeaknessOut

router = APIRouter(prefix="/pokemon", tags=["Pokemon"])


# ============================================================
# 🔹 Pokémon list
# ============================================================
@router.get("/", response_model=List[PokemonListItem])
def get_pokemon_list(db: Session = Depends(get_db)):
    """
    List all Pokémon from the database.

    Returns a comprehensive list of all available Pokémon including:
    - Basic information (ID, species, form)
    - Types (primary and secondary)
    - Sprite URL for visual display

    This endpoint is designed for Pokémon selection interfaces (dropdowns, grids).

    **Returns:**
    - List of Pokémon with:
      - id: Pokémon unique identifier
      - form: Form name (normal, alola, mega, etc.)
      - species: Species name
      - sprite_url: URL to Pokémon sprite image
      - types: List of types (1 or 2)

    **Example Response:**
    ```json
    [
      {
        "id": 25,
        "form": {"id": 1, "name": "normal"},
        "species": "Pikachu",
        "sprite_url": "https://...",
        "types": [
          {"slot": 1, "name": "Electric"}
        ]
      }
    ]
    ```

    **Use Case:**
    Populate Pokémon selection lists in the Streamlit interface.
    """
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
# ⚠️ Must be defined before /{pokemon_id} route
# ============================================================
@router.get("/search", response_model=List[PokemonListItem])
def search_pokemon(
    name: str = Query(..., min_length=1),
    lang: str = Query("fr", pattern="^(fr|en|jp)$"),
    db: Session = Depends(get_db),
):
    """
    Search for Pokémon by species name (partial or full match).

    This endpoint performs a case-insensitive partial match on Pokémon species names.
    Designed to be Streamlit-friendly by returning an empty list instead of 404
    when no matches are found.

    **Query Parameters:**
    - name: Species name to search (minimum 1 character, partial match supported)
    - lang: Language code for search (default: "fr")
      - "fr": French names (e.g., "Pikachu", "Dracaufeu")
      - "en": English names (e.g., "Pikachu", "Charizard")
      - "jp": Japanese names (e.g., "ピカチュウ")

    **Returns:**
    - List of matching Pokémon (empty list if no matches)
    - Each entry includes: id, form, species, sprite_url, types

    **Example Request:**
    ```
    GET /pokemon/search?name=pika&lang=fr
    ```

    **Example Response:**
    ```json
    [
      {
        "id": 25,
        "form": {"id": 1, "name": "normal"},
        "species": "Pikachu",
        "sprite_url": "https://...",
        "types": [{"slot": 1, "name": "Electric"}]
      }
    ]
    ```

    **Note:**
    - No 404 error if no match (returns empty list)
    - Optimized for autocomplete and search-as-you-type interfaces
    """
    pokemons = search_pokemon_by_species_name(db, name=name, lang=lang)

    # No 404 error here - Streamlit-friendly
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
    """
    Get detailed information for a specific Pokémon by ID.

    Returns comprehensive data about a Pokémon including:
    - Base stats (HP, Attack, Defense, Special Attack, Special Defense, Speed)
    - Types and type effectiveness
    - Physical characteristics (height, weight)
    - Complete move list with learning methods
    - Sprite URL for display

    **Path Parameters:**
    - pokemon_id: Unique Pokémon identifier (1-188)

    **Returns:**
    - id: Pokémon unique identifier
    - form: Form information (normal, alola, mega, giga)
    - species: Species name
    - stats: Dictionary with 6 base stats
    - height_m: Height in meters
    - weight_kg: Weight in kilograms
    - sprite_url: URL to Pokémon sprite
    - types: List of types (1 or 2)
    - moves: Complete move list with:
      - name: Move name
      - type: Move type
      - category: Physical/Special/Status
      - learn_method: Level-up/TM/Egg/Tutor
      - learn_level: Level learned (if applicable)
      - power: Move power
      - accuracy: Move accuracy (%)

    **Example Response:**
    ```json
    {
      "id": 25,
      "form": {"id": 1, "name": "normal"},
      "species": "Pikachu",
      "stats": {"hp": 35, "attack": 55, "defense": 40, "sp_attack": 50, "sp_defense": 50, "speed": 90},
      "height_m": 0.4,
      "weight_kg": 6.0,
      "sprite_url": "https://...",
      "types": [{"slot": 1, "name": "Electric"}],
      "moves": [...]
    }
    ```

    **Errors:**
    - 404: Pokémon not found (invalid ID)

    **Use Case:**
    Display Pokémon details in the Streamlit interface (stats, moves, types).
    """
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
    """
    Get type effectiveness (weaknesses and resistances) for a specific Pokémon.

    Computes the cumulative type effectiveness multipliers based on the Pokémon's
    types (single or dual-type). Returns all 18 types with their effectiveness
    multipliers against this Pokémon.

    **How it works:**
    - Single-type Pokémon: Direct lookup from type effectiveness table
    - Dual-type Pokémon: Multiplies effectiveness of both types
      - Example: Charizard (Fire/Flying) vs Water = 2.0 × 1.0 = 2.0 (double weakness)

    **Path Parameters:**
    - pokemon_id: Unique Pokémon identifier (1-188)

    **Returns:**
    List of type effectiveness with:
    - type_name: Attacking type name
    - multiplier: Damage multiplier (0, 0.25, 0.5, 1.0, 2.0, 4.0)
      - 0.0 = Immune (no effect)
      - 0.25 = Double resistance
      - 0.5 = Resisted (not very effective)
      - 1.0 = Neutral
      - 2.0 = Weak (super effective)
      - 4.0 = Double weakness

    **Example Response:**
    ```json
    [
      {"type_name": "Water", "multiplier": 2.0},
      {"type_name": "Electric", "multiplier": 2.0},
      {"type_name": "Rock", "multiplier": 4.0},
      {"type_name": "Ground", "multiplier": 0.0},
      {"type_name": "Fire", "multiplier": 0.5}
    ]
    ```

    **Errors:**
    - 404: Pokémon not found (invalid ID)

    **Use Case:**
    Display type matchup chart in Pokémon details page (weaknesses in red, resistances in green).
    """
    weaknesses = compute_pokemon_weaknesses(db, pokemon_id)

    if weaknesses is None:
        raise HTTPException(
            status_code=404,
            detail="Pokemon not found",
        )

    return weaknesses
