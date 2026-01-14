# app/schemas/formatters/pokemon_ui.py

from pydantic import BaseModel, ConfigDict
from typing import Optional


class PokemonSelectItem(BaseModel):
    """
    Minimal Pokémon representation for UI selectors (Streamlit).
    """
    id: int
    name: str
    sprite_url: Optional[str]

    model_config = ConfigDict(from_attributes=True)
