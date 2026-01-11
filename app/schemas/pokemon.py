from typing import List, Optional
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

from app.schemas.pokemon_species import PokemonSpeciesOut
from app.schemas.pokemon_type import PokemonTypeOut


# -------------------------
# 🔹 Stats
# -------------------------
class PokemonStatsOut(BaseModel):
    hp: int
    attack: int
    defense: int
    sp_attack: int
    sp_defense: int
    speed: int

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# 🔹 Moves (vue Pokémon)
# -------------------------
class PokemonMoveOut(BaseModel):
    name: str
    type: str
    learn_method: str
    learn_level: Optional[int]

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# 🔹 Base Pokémon
# -------------------------
class PokemonBase(BaseModel):
    id: int
    form_name: str
    is_mega: bool
    is_alola: bool
    is_starter: bool

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# 🔹 Pokémon - liste
# -------------------------
class PokemonListItem(PokemonBase):
    species: PokemonSpeciesOut
    types: List[PokemonTypeOut]
    sprite_url: Optional[str]


# -------------------------
# 🔹 Pokémon - détail
# -------------------------
class PokemonDetail(PokemonBase):
    species: PokemonSpeciesOut
    stats: PokemonStatsOut
    types: List[PokemonTypeOut]
    moves: List[PokemonMoveOut]

    height_m: Decimal
    weight_kg: Decimal
    sprite_url: Optional[str]


# -------------------------
# 🔹 Réponse paginée
# -------------------------
class PokemonListResponse(BaseModel):
    count: int
    results: List[PokemonListItem]
