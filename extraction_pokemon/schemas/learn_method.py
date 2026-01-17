# extraction_pokemon/schemas/learn_method.py

"""
Pydantic schema – LearnMethod
==============================

Defines the output schema for a Pokémon LearnMethod.
This schema is used in FastAPI responses to serialize
learn method data from the database.

Fields:
- id    : unique identifier of the learn method
- name  : normalized name of the method (e.g., level_up, ct, move_tutor)
"""

from pydantic import BaseModel, ConfigDict


class LearnMethodOut(BaseModel):
    """
    Output schema for LearnMethod.

    Ensures consistent serialization of LearnMethod objects
    in API responses, with attribute-based mapping.
    """
    id: int
    name: str  # level_up | ct | move_tutor | etc.

    model_config = ConfigDict(from_attributes=True)
