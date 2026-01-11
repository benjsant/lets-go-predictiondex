"""
Pydantic schema – Type effectiveness
===================================

This module defines the Pydantic schema used to expose Pokémon type
effectiveness data through the API.

Type effectiveness represents the damage multiplier applied when a move
of a given attacking type hits a Pokémon of a given defending type.

This schema is a direct, read-only representation of the
`type_effectiveness` relational table and is primarily used for:
- damage calculation logic,
- battle simulations,
- analytical and educational endpoints.

Example multipliers:
- 0.00 → no effect
- 0.50 → not very effective
- 1.00 → neutral damage
- 2.00 → super effective
"""

from pydantic import BaseModel, ConfigDict
from decimal import Decimal


class TypeEffectivenessOut(BaseModel):
    """
    Output schema representing a type effectiveness relationship.

    Each instance describes how effective an attacking type is
    against a defending type using a numeric multiplier.
    """
    attacking_type_id: int
    defending_type_id: int
    multiplier: Decimal

    model_config = ConfigDict(from_attributes=True)
