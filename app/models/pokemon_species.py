from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base


class PokemonSpecies(Base):
    __tablename__ = "pokemon_species"

    id = Column(Integer, primary_key=True)
    pokedex_number = Column(Integer, nullable=False, index=True)

    name_fr = Column(String(75), nullable=False)
    name_en = Column(String(75))

    pokemons = relationship(
        "Pokemon",
        back_populates="species",
        cascade="all, delete-orphan",
    )
