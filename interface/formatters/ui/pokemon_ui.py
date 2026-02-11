# /interface/formatters/ui/pokemon_ui.py

from typing import Dict, List, Optional

from pydantic import BaseModel


class PokemonSelectItem(BaseModel):
    """Pydantic model for a Pokemon in the Streamlit UI."""
    id: int
    name: str
    pokedex_number: Optional[int] = None
    sprite_url: Optional[str] = None
    types: List[str] = []
    stats: Optional[Dict[str, int]] = None
    total_stats: Optional[int] = None
    height_m: Optional[str] = None
    weight_kg: Optional[str] = None
