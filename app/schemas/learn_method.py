# app/schemas/learn_method.py

from pydantic import BaseModel, ConfigDict


class LearnMethodOut(BaseModel):
    id: int
    name: str  # level_up | ct | move_tutor | etc.

    model_config = ConfigDict(from_attributes=True)
