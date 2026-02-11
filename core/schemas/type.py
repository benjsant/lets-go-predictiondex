# core/schemas/type.py
"""Pydantic schemas for Pokemon types."""

from typing import List

from pydantic import BaseModel, ConfigDict


class TypeOut(BaseModel):
 """Basic Pokemon type (id + name)."""

 id: int
 name: str

 model_config = ConfigDict(from_attributes=True)


class TypeWithMoves(TypeOut):
 """Pokemon type with associated move IDs."""

 move_ids: List[int] = []

 model_config = ConfigDict(from_attributes=True)
