# app/schemas/pokemon_move.py

"""
Pydantic schemas – PokemonMove
==============================

This module defines the Pydantic schema used to expose the relationship
between a Pokémon and a move in the FastAPI layer.

The schema represents **how a Pokémon learns a specific move**, including:
- the move itself,
- the learning method (level-up, TM, move tutor, etc.),
- the optional learning level.

This schema is typically nested inside Pokémon-related API responses
and mirrors the `PokemonMove` SQLAlchemy association model.
"""

from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.schemas.learn_method import LearnMethodOut
from app.schemas.move import MoveListItem


class PokemonMoveOut(BaseModel):
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
