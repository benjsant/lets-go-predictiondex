"""
Pydantic schemas – Pokémon types
================================

This module defines the Pydantic schemas used to expose Pokémon elemental
types through the API.

A Pokémon type (e.g. Fire, Water, Electric) is a core battle mechanic that:
- determines move effectiveness,
- influences damage multipliers,
- drives type-based analytics and simulations.

These schemas are read-only and map directly to the underlying
SQLAlchemy `Type` model.
"""

from pydantic import BaseModel, ConfigDict
from typing import List


# -------------------------
# 🔹 Basic Type
# -------------------------
class TypeOut(BaseModel):
    """
    Basic output schema for a Pokémon elemental type.

    This schema is typically used in:
    - Pokémon listings,
    - move descriptions,
    - lightweight API responses.
    """

    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# 🔹 Type with moves (optional)
# -------------------------
class TypeWithMoves(TypeOut):
    """
    Extended type schema including related move identifiers.

    This schema is useful for:
    - analytical endpoints,
    - debugging or data inspection,
    - future extensions linking types to their moves.
    """

    move_ids: List[int]
