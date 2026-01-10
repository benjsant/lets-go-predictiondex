from pydantic import BaseModel, ConfigDict
from typing import Optional


# -------------------------
# 🔹 Pokémon Species
# -------------------------
class PokemonSpeciesOut(BaseModel):
    id: int
    pokedex_number: int
    name_fr: str
    name_en: Optional[str]

    model_config = ConfigDict(from_attributes=True)
