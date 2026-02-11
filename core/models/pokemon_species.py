# core/models/pokemon_species.py
"""SQLAlchemy model for Pokemon species (Pokedex entries)."""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from core.db.base import Base


class PokemonSpecies(Base):
    """
    Pokémon species entity.

    This table stores species-level information that is common to all forms
    of a Pokémon, independently of gameplay mechanics or form-specific data.

    Business rules:
    - Each species has a unique Pokédex number.
    - A species can have one or many Pokémon forms.
    - Deleting a species cascades to all related Pokémon forms.

    This model is used as:
    - a canonical Pokédex reference,
    - a grouping entity for Pokémon forms,
    - a stable join target for analytics and ML pipelines.
    """

    __tablename__ = "pokemon_species"

    #: Primary key
    id = Column(Integer, primary_key=True)

    #: National Pokédex number (indexed for fast lookup)
    pokedex_number = Column(Integer, nullable=False, index=True)

    #: French display name of the species
    name_fr = Column(String(75), nullable=False)

    #: English display name of the species (optional)
    name_en = Column(String(75))

    #: All Pokémon forms belonging to this species
    pokemons = relationship(
        "Pokemon",
        back_populates="species",
        cascade="all, delete-orphan",
    )
