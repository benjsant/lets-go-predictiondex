# core/schemas/pokemon_type.py
"""
Pydantic schemas – Pokémon Type
===============================

This module defines the Pydantic schema used to expose Pokémon type
information through the FastAPI API layer.

A Pokémon type represents an elemental attribute (e.g. Fire, Water,
Electric) assigned to a Pokémon, with support for mono-type and dual-type
configurations via ordered slots.
"""

from pydantic import BaseModel, ConfigDict


class PokemonTypeOut(BaseModel):
    """
    Output schema representing a Pokémon type assignment.

    Attributes:
    - `slot`: Position of the type (1 = primary, 2 = secondary).
    - `name`: Normalized name of the elemental type.

    This schema is designed to be API-friendly and is commonly embedded
    in Pokémon-related responses.
    """
    slot: int
    name: str

    model_config = ConfigDict(from_attributes=True)
