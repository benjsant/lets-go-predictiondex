# api_pokemon/routes/type_route.py
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
# 🔹 Types
# -------------------------------------------------------------------
@router.get("/", response_model=List[TypeOut])
def get_types(db: Session = Depends(get_db)):
    """
    List all Pokémon elemental types.

    Returns the complete list of 18 Pokémon types available in the game.

    **Returns:**
    List of types with:
    - id: Type unique identifier (1-18)
    - name: Type name (Normal, Fire, Water, Electric, Grass, Ice, Fighting, Poison,
            Ground, Flying, Psychic, Bug, Rock, Ghost, Dragon, Dark, Steel, Fairy)

    **Example Response:**
    ```json
    [
      {"id": 1, "name": "Normal"},
      {"id": 2, "name": "Fire"},
      {"id": 3, "name": "Water"}
    ]
    ```

    **Use Case:**
    Populate type filters and type effectiveness charts.
    """
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
    """
    Get type effectiveness data by type IDs.

    Query the type effectiveness chart (18×18 matrix) to determine damage multipliers
    for attack/defense type combinations. Supports filtering by attacking type,
    defending type, or both.

    **Query Parameters:**
    - attacking_type_id (optional): Filter by attacking type ID (1-18)
    - defending_type_id (optional): Filter by defending type ID (1-18)
    - If both provided: Returns single effectiveness entry
    - If one provided: Returns all matchups for that type
    - If none provided: Returns complete 18×18 effectiveness matrix (324 entries)

    **Returns:**
    List of type effectiveness with:
    - attacking_type_id: Attacker type ID
    - attacking_type_name: Attacker type name
    - defending_type_id: Defender type ID
    - defending_type_name: Defender type name
    - multiplier: Damage multiplier (0, 0.5, 1, 2)
      - 0.0 = No effect (immune)
      - 0.5 = Not very effective (resisted)
      - 1.0 = Normal damage
      - 2.0 = Super effective

    **Example Response:**
    ```json
    [
      {
        "attacking_type_id": 2,
        "attacking_type_name": "Fire",
        "defending_type_id": 3,
        "defending_type_name": "Water",
        "multiplier": 0.5
      }
    ]
    ```

    **Errors:**
    - 404: No type effectiveness found for given parameters

    **Use Case:**
    Build type effectiveness charts and battle strategy helpers.
    """
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
    """
    Get type effectiveness data by type names.

    Same as /affinities endpoint but accepts type names instead of IDs.
    More user-friendly for Streamlit interfaces and manual queries.

    **Query Parameters:**
    - attacking (optional): Attacking type name (e.g., "Fire", "Water", "Electric")
    - defending (optional): Defending type name (e.g., "Grass", "Rock", "Dragon")
    - If both provided: Returns single effectiveness entry
    - If one provided: Returns all matchups for that type
    - If none provided: Returns complete effectiveness matrix (324 entries)

    **Returns:**
    List of type effectiveness (same format as /affinities endpoint)

    **Example Request:**
    ```
    GET /types/affinities/by-name?attacking=Fire&defending=Grass
    ```

    **Example Response:**
    ```json
    [
      {
        "attacking_type_id": 2,
        "attacking_type_name": "Fire",
        "defending_type_id": 5,
        "defending_type_name": "Grass",
        "multiplier": 2.0
      }
    ]
    ```

    **Errors:**
    - 404: No type effectiveness found (invalid type names)

    **Use Case:**
    Streamlit type effectiveness calculator and battle strategy page.
    """
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
# ⚠️ Must be defined before /{type_id} route
# -------------------------------------------------------------------
@router.get("/by-name/{type_name}/pokemon", response_model=List[PokemonListItem])
def get_pokemon_by_type_name(
    type_name: str,
    db: Session = Depends(get_db),
):
    """
    List all Pokémon of a specific type (by type name).

    Returns all Pokémon that have the specified type as either their primary
    or secondary type. User-friendly alternative to type ID-based search.

    **Path Parameters:**
    - type_name: Type name (e.g., "Fire", "Water", "Electric", "Dragon")
      - Case-insensitive
      - Matches exact type name

    **Returns:**
    List of Pokémon with:
    - id: Pokémon unique identifier
    - form: Form information
    - species: Species name
    - sprite_url: Sprite image URL
    - types: List of types (1 or 2)

    **Example Request:**
    ```
    GET /types/by-name/Fire/pokemon
    ```

    **Example Response:**
    ```json
    [
      {
        "id": 4,
        "form": {"id": 1, "name": "normal"},
        "species": "Charmander",
        "sprite_url": "https://...",
        "types": [{"slot": 1, "name": "Fire"}]
      },
      {
        "id": 6,
        "form": {"id": 1, "name": "normal"},
        "species": "Charizard",
        "sprite_url": "https://...",
        "types": [
          {"slot": 1, "name": "Fire"},
          {"slot": 2, "name": "Flying"}
        ]
      }
    ]
    ```

    **Errors:**
    - 404: No Pokémon found for this type (invalid type name or no matches)

    **Use Case:**
    Filter Pokémon by type in Streamlit interface (type-based team building).
    """
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
    """
    List all Pokémon of a specific type (by type ID).

    Returns all Pokémon that have the specified type as either their primary
    or secondary type. Faster than name-based search (direct ID lookup).

    **Path Parameters:**
    - type_id: Type unique identifier (1-18)
      - 1 = Normal, 2 = Fire, 3 = Water, 4 = Electric, 5 = Grass, etc.

    **Returns:**
    List of Pokémon (same format as /by-name/{type_name}/pokemon)

    **Example Request:**
    ```
    GET /types/2/pokemon
    ```

    **Example Response:**
    ```json
    [
      {
        "id": 4,
        "form": {"id": 1, "name": "normal"},
        "species": "Charmander",
        "sprite_url": "https://...",
        "types": [{"slot": 1, "name": "Fire"}]
      }
    ]
    ```

    **Errors:**
    - 404: No Pokémon found for this type (invalid type ID)

    **Use Case:**
    Programmatic filtering when type ID is already known (faster than name lookup).
    """
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
