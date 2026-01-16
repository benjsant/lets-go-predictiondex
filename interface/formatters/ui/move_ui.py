# app/formatters/ui/move_ui.py

from pydantic import BaseModel
from typing import Optional

class MoveSelectItem(BaseModel):
    """
    Pydantic model for Pokémon moves in Streamlit.
    """
    id: Optional[int] = None
    name: str
    label: str
    type: str
    category: str
    learn_method: Optional[str] = None
    learn_level: Optional[int] = None

