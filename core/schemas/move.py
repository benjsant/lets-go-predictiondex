# core/schemas/move.py
"""Pydantic schemas for Pokemon moves."""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from core.schemas.type import TypeOut


# -------------------------
# Base Move
# -------------------------
class MoveBase(BaseModel):
    """
    Base schema for a Pokémon move.

    Contains the minimal shared attributes used across
    multiple API responses.
    """
    id: int
    name: str
    category: str
    type: TypeOut

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# Move – list view
# -------------------------
class MoveListItem(MoveBase):
    """
    Lightweight schema for listing moves.

    Used in collection endpoints where only
    key combat-relevant information is required.
    """
    power: Optional[int]
    accuracy: Optional[int]
    description: Optional[str] = None


# -------------------------
# Move – detail view
# -------------------------
class MoveDetail(MoveListItem):
    """
    Detailed schema for a single move.

    Extends the list view with descriptive
    and behavioral fields.
    """
    description: Optional[str]
    damage_type: Optional[str]


# -------------------------
# Pokémon learning the move (Move-centric view)
# -------------------------
class MovePokemonOut(BaseModel):
    """
    Schema representing a Pokémon that can learn a given move.

    This is a move-centric perspective, used when displaying
    all Pokémon capable of learning a specific move.
    """
    pokedex_number: int
    name_fr: str
    form_name: str
    learn_method: str
    learn_level: Optional[int]

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# Move with Pokémon list
# -------------------------
class MoveWithPokemons(MoveDetail):
    """
    Detailed move schema including all Pokémon
    that can learn the move.

    Used in endpoints such as:
    - GET /moves/{id}
    """
    pokemons: List[MovePokemonOut]


class MoveSelectableOut(BaseModel):
    """
    Move formatted for Pokémon move selection (Streamlit / ML input).
    """
    id: int
    name: str
    category: str
    power: Optional[int]
    accuracy: Optional[int]
    description: Optional[str] = None

    type: TypeOut

    # Pokémon-specific fields
    learn_method: Optional[str] = None
    learn_level: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
