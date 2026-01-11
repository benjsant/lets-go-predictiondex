# app/schemas/type_effectiveness.py

from pydantic import BaseModel, ConfigDict
from decimal import Decimal


class TypeEffectivenessOut(BaseModel):
    attacking_type_id: int
    defending_type_id: int
    multiplier: Decimal

    model_config = ConfigDict(from_attributes=True)
