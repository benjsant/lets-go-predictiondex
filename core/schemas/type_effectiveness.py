# core/schemas/type_effectiveness.py
"""Pydantic schemas for type effectiveness (damage multipliers)."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class TypeEffectivenessOut(BaseModel):
 """Type effectiveness with IDs and damage multiplier."""

 attacking_type_id: int
 defending_type_id: int
 multiplier: Decimal

 model_config = ConfigDict(from_attributes=True)


class TypeEffectivenessDetailedOut(BaseModel):
 """Type effectiveness with type names instead of IDs."""

 attacking_type: str
 defending_type: str
 multiplier: Decimal

 model_config = ConfigDict(from_attributes=True)
