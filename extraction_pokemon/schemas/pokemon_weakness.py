from pydantic import BaseModel, ConfigDict
from decimal import Decimal


class PokemonWeaknessOut(BaseModel):
    """
    Damage multiplier applied to this Pokémon
    when hit by a move of the given attacking type.
    """
    attacking_type: str
    multiplier: Decimal

    model_config = ConfigDict(from_attributes=True)
