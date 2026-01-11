# app/schemas/pokemon_move.py

from pydantic import BaseModel, ConfigDict
from typing import Optional

from app.schemas.learn_method import LearnMethodOut
from app.schemas.move import MoveListItem


class PokemonMoveOut(BaseModel):
    move: MoveListItem
    learn_method: LearnMethodOut
    learn_level: Optional[int]

    model_config = ConfigDict(from_attributes=True)

