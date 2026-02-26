"""Pydantic schemas for Pokemon moves."""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from core.schemas.type import TypeOut


class MoveBase(BaseModel):
    """Base schema for a Pokémon move."""
    id: int
    name: str
    category: str
    type: TypeOut

    model_config = ConfigDict(from_attributes=True)


class MoveListItem(MoveBase):
    """Lightweight schema for listing moves."""
    power: Optional[int]
    accuracy: Optional[int]
    description: Optional[str] = None


class MoveDetail(MoveListItem):
    """Detailed schema for a single move."""
    description: Optional[str]
    damage_type: Optional[str]


class MovePokemonOut(BaseModel):
    """Schema representing a Pokémon that can learn a given move."""
    pokedex_number: int
    name_fr: str
    form_name: str
    learn_method: str
    learn_level: Optional[int]

    model_config = ConfigDict(from_attributes=True)


class MoveWithPokemons(MoveDetail):
    """Detailed move schema including all Pokémon that can learn the move."""
    pokemons: List[MovePokemonOut]


class MoveSelectableOut(BaseModel):
    """Move formatted for Pokémon move selection (Streamlit / ML input)."""
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
