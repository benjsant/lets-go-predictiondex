# app/schemas/type.py

from pydantic import BaseModel, ConfigDict
from typing import List


# -------------------------
# 🔹 Type simple
# -------------------------
class TypeOut(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# 🔹 Type avec moves (optionnel)
# -------------------------
class TypeWithMoves(TypeOut):
    move_ids: List[int]
