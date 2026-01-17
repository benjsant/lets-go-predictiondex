# formatters/ui/pokemon_ui.py

from pydantic import BaseModel
from typing import Optional, List

class PokemonSelectItem(BaseModel):
    """
    Pydantic model for Pokémon selector in Streamlit.
    """
    id: int
    name: str
    sprite_url: Optional[str] = None
    types: List[str] = []
