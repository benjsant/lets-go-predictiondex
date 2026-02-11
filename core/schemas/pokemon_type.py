# core/schemas/pokemon_type.py
"""Pydantic schema for Pokemon type assignment."""

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
