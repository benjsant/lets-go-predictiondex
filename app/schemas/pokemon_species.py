"""
Pydantic schemas – Pokémon Species
=================================

This module defines the Pydantic schema used to expose Pokémon species
data through the FastAPI API layer.

A Pokémon species represents the **base Pokédex entry**, independent of:
- forms (Mega, Alolan, etc.),
- gameplay-specific variations,
- learning mechanics.

This schema is typically embedded in Pokémon-related responses and
serves as a stable reference for Pokédex-level information.
"""

from typing import Optional
from pydantic import BaseModel, ConfigDict


class PokemonSpeciesOut(BaseModel):
    """
    Output schema representing a Pokémon species.

    This schema exposes canonical Pokédex data such as the Pokédex number
    and localized species names. It is independent from Pokémon forms
    and gameplay attributes.
    """
    id: int
    pokedex_number: int
    name_fr: str
    name_en: Optional[str]

    model_config = ConfigDict(from_attributes=True)
