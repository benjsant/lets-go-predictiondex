# core/schemas/form.py
from pydantic import BaseModel, ConfigDict

class FormOut(BaseModel):
    """
    Output schema representing a Pokémon form.

    Attributes:
        id (int): Unique identifier of the form.
        name (str): Name of the form (e.g., base, mega, alola, starter).

    Designed to be read-only and built from SQLAlchemy ORM objects.
    """
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)
