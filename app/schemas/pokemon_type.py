from pydantic import BaseModel, ConfigDict


# -------------------------
# 🔹 Type Pokémon (API friendly)
# -------------------------
class PokemonTypeOut(BaseModel):
    slot: int
    name: str

    model_config = ConfigDict(from_attributes=True)
