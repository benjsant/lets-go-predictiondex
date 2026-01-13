# app/schemas/pokemon.py
"""
Pydantic schemas – Pokémon
=========================

This module defines the Pydantic schemas used to expose Pokémon-related
data through the FastAPI API layer.

A Pokémon represents a concrete playable form of a species
(Base, Mega, Alola, Starter, etc.).

These schemas are read-only output models, built from SQLAlchemy ORM
objects and optimized for clean, stable API contracts.
"""

from typing import List, Optional
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

from app.schemas.pokemon_species import PokemonSpeciesOut
from app.schemas.pokemon_type import PokemonTypeOut
from app.schemas.form import FormOut


# -------------------------
# 🔹 Stats
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
# 🔹 Moves (Pokémon-centric view)
# -------------------------
class PokemonMoveOut(BaseModel):
    """
    Output schema representing a move learned by a Pokémon.
    """
    name: str
    type: str
    category: str  # 🔹 nouvelle propriété pour la catégorie du move
    learn_method: str
    learn_level: Optional[int]

    model_config = ConfigDict(from_attributes=True)



# -------------------------
# 🔹 Base Pokémon
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
# 🔹 Pokémon – list view
# -------------------------
class PokemonListItem(PokemonBase):
    """
    Lightweight Pokémon representation for list endpoints.
    """
    species: PokemonSpeciesOut
    types: List[PokemonTypeOut]
    sprite_url: Optional[str]


# -------------------------
# 🔹 Pokémon – detail view
# -------------------------
class PokemonDetail(PokemonBase):
    """
    Full Pokémon representation for detail endpoints.
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
