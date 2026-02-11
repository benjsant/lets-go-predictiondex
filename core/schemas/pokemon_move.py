# core/schemas/pokemon_move.py
"""Pydantic schema for Pokemon move learning associations."""

from typing import Optional

from pydantic import BaseModel, ConfigDict

from core.schemas.learn_method import LearnMethodOut
from core.schemas.move import MoveListItem


class PokemonMoveORMOut(BaseModel):
    """
    Output schema representing a move learned by a Pokémon.

    This schema is a read-only representation of the enriched
    Pokémon ↔ Move association and is used in endpoints such as:
    - GET /pokemons/{id}
    - GET /pokemons/{id}/moves
    """
    move: MoveListItem
    learn_method: LearnMethodOut
    learn_level: Optional[int]

    model_config = ConfigDict(from_attributes=True)
