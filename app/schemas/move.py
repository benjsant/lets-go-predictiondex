# app/schemas/move.py

from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.schemas.type import TypeOut


# -------------------------
# 🔹 Base Move
# -------------------------
class MoveBase(BaseModel):
    id: int
    name: str
    category: str
    type: TypeOut

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# 🔹 Move - liste
# -------------------------
class MoveListItem(MoveBase):
    power: Optional[int]
    accuracy: Optional[int]


# -------------------------
# 🔹 Move - détail
# -------------------------
class MoveDetail(MoveListItem):
    description: Optional[str]
    damage_type: Optional[str]


# -------------------------
# 🔹 Pokémon apprenant le move (vue Move)
# -------------------------
class MovePokemonOut(BaseModel):
    pokedex_number: int
    name_fr: str
    form_name: str
    learn_method: str
    learn_level: Optional[int]

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# 🔹 Move avec Pokémon
# -------------------------
class MoveWithPokemons(MoveDetail):
    pokemons: List[MovePokemonOut]
