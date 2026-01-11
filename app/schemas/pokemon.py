"""
Pydantic schemas – Pokémon
=========================

This module defines the Pydantic schemas used to expose Pokémon-related
data through the FastAPI API layer.

It covers multiple representation levels:
- base Pokémon identity and form flags,
- statistics and physical attributes,
- elemental types,
- learnable moves,
- list and detail API responses.

These schemas are read-only output models, built from SQLAlchemy ORM
objects and optimized for clean, stable API contracts.
"""

from typing import List, Optional
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

from app.schemas.pokemon_species import PokemonSpeciesOut
from app.schemas.pokemon_type import PokemonTypeOut


# -------------------------
# 🔹 Stats
# -------------------------
class PokemonStatsOut(BaseModel):
    """
    Output schema representing a Pokémon's base stats.

    Includes all six standard Pokémon statistics used for
    battle mechanics and analysis.
    """
    hp: int
    attack: int
    defense: int
    sp_attack: int
    sp_defense: int
    speed: int

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# 🔹 Moves (Pokémon view)
# -------------------------
class PokemonMoveOut(BaseModel):
    """
    Output schema representing a move learned by a Pokémon.

    This view is Pokémon-centric and focuses on how the move
    is learned rather than on the move's full technical details.
    """
    name: str
    type: str
    learn_method: str
    learn_level: Optional[int]

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# 🔹 Base Pokémon
# -------------------------
class PokemonBase(BaseModel):
    """
    Base Pokémon schema containing identity and form-related flags.

    Used as a shared parent for list and detail representations.
    """
    id: int
    form_name: str
    is_mega: bool
    is_alola: bool
    is_starter: bool

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# 🔹 Pokémon – list view
# -------------------------
class PokemonListItem(PokemonBase):
    """
    Lightweight Pokémon representation used in list endpoints.
    """
    species: PokemonSpeciesOut
    types: List[PokemonTypeOut]
    sprite_url: Optional[str]


# -------------------------
# 🔹 Pokémon – detail view
# -------------------------
class PokemonDetail(PokemonBase):
    """
    Full Pokémon representation used in detail endpoints.

    Includes combat statistics, learnable moves, physical attributes,
    and elemental typing.
    """
    species: PokemonSpeciesOut
    stats: PokemonStatsOut
    types: List[PokemonTypeOut]
    moves: List[PokemonMoveOut]

    height_m: Decimal
    weight_kg: Decimal
    sprite_url: Optional[str]


# -------------------------
# 🔹 Paginated response
# -------------------------
class PokemonListResponse(BaseModel):
    """
    Paginated response wrapper for Pokémon list endpoints.
    """
    count: int
    results: List[PokemonListItem]
