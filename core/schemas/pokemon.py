# core/schemas/pokemon.py
"""Pydantic schemas for Pokemon API responses."""

from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from core.schemas.form import FormOut
from core.schemas.pokemon_species import PokemonSpeciesOut
from core.schemas.pokemon_type import PokemonTypeOut


# -------------------------
# Stats
# -------------------------
class PokemonStatsOut(BaseModel):
    """
    Output schema representing a Pokémon's base stats.
    """
    hp: int
    attack: int
    defense: int
    sp_attack: int
    sp_defense: int
    speed: int

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# Moves (Pokémon-centric view)
# -------------------------
class PokemonMoveUIOut(BaseModel):
    """
    Flattened move schema for UI / Streamlit usage.
    """
    name: str
    type: str
    category: str
    learn_method: str
    learn_level: Optional[int]
    power: Optional[int]
    accuracy: Optional[int]
    damage_type: Optional[str]

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# Base Pokémon
# -------------------------
class PokemonBase(BaseModel):
    """
    Base Pokémon schema.

    Represents a concrete Pokémon form.
    """
    id: int
    form: FormOut

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# Pokémon – list view
# -------------------------
class PokemonListItem(PokemonBase):
    """
    Lightweight Pokémon representation for list endpoints.
    """
    species: PokemonSpeciesOut
    types: List[PokemonTypeOut]
    sprite_url: Optional[str]


# -------------------------
# Pokémon – detail view
# -------------------------
class PokemonDetail(PokemonBase):
    """
    Full Pokémon representation for detail endpoints.
    """
    species: PokemonSpeciesOut
    stats: PokemonStatsOut
    types: List[PokemonTypeOut]
    moves: List[PokemonMoveUIOut]

    height_m: Decimal
    weight_kg: Decimal
    sprite_url: Optional[str]


# -------------------------
# Paginated response
# -------------------------
class PokemonListResponse(BaseModel):
    """
    Paginated response wrapper for Pokémon list endpoints.
    """
    count: int
    results: List[PokemonListItem]
