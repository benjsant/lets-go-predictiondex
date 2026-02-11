# core/schemas/pokemon_species.py
"""Pydantic schema for Pokemon species."""

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
