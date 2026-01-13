# app/schemas/move_category.py
from pydantic import BaseModel, ConfigDict

class MoveCategoryOut(BaseModel):
    """
    Output schema representing a Pokémon move category.

    Attributes:
        id (int): Unique identifier of the move category.
        name (str): Name of the category (e.g., physique, spécial, autre).

    Designed to be read-only and built from SQLAlchemy ORM objects.
    """
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)
