# extraction_pokemon/models/pokemon.py

"""
SQLAlchemy Model – Pokemon
=========================

This module defines the `Pokemon` model, which represents a **specific Pokémon
form** in the database for Pokémon Let's Go Pikachu / Eevee.

A Pokémon instance corresponds to a concrete, playable form of a species
(e.g. Base form, Mega Evolution, Alolan form), and not to the species itself.

The model is designed to:
- normalize data coming from multiple sources (PokeAPI, Poképédia),
- support form-specific attributes and flags,
- serve as a core entity for battle simulation and machine learning.

Each Pokémon:
- belongs to exactly one species,
- can have stats, types, and learnable moves,
- is uniquely identified by its species and form name.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    Text,
    ForeignKey,
    UniqueConstraint,
    TIMESTAMP,
    func,
)
from sqlalchemy.orm import relationship
from extraction_pokemon.db.base import Base


class Pokemon(Base):
    """
    Pokémon entity representing a specific form of a species.

    This table stores form-level data for Pokémon, including physical
    characteristics, form flags, and technical identifiers used for scraping
    and cross-dataset comparison.

    Business rules:
    - A species can have multiple forms.
    - Each (species_id, form_name) combination must be unique.
    - Deleting a species cascades to all its Pokémon forms.

    This model is central to:
    - move learning history,
    - type assignments,
    - stat storage,
    - battle simulation and ML feature generation.
    """

    __tablename__ = "pokemon"

    #: Primary key
    id = Column(Integer, primary_key=True)

    #: Foreign key to the Pokémon species
    species_id = Column(
        Integer,
        ForeignKey("pokemon_species.id", ondelete="CASCADE"),
        nullable=False,
    )

    # --- Technical identifiers (scraping / API / comparisons) ---

    #: Normalized Pokémon name from PokeAPI (unique)
    name_pokeapi = Column(String(100), nullable=False, unique=True)

    #: Pokémon name as displayed on Poképédia
    name_pokepedia = Column(String(150), nullable=False)

    #: Foreign key to Form
    form_id = Column(Integer, ForeignKey("form.id", ondelete="CASCADE"), nullable=False)

    # --- Physical characteristics ---

    #: Height in meters
    height_m = Column(Numeric(5, 2), nullable=False)

    #: Weight in kilograms
    weight_kg = Column(Numeric(5, 2), nullable=False)

    #: URL to the Pokémon sprite or official artwork
    sprite_url = Column(Text)

    #: Record creation timestamp
    created_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
    )

    # --- Relationships ---

    #: Species this Pokémon form belongs to
    species = relationship(
        "PokemonSpecies",
        back_populates="pokemons",
    )

    #: Base stats associated with this Pokémon (1–1)
    stats = relationship(
        "PokemonStat",
        back_populates="pokemon",
        uselist=False,
        cascade="all, delete-orphan",
    )

    #: Elemental types of the Pokémon (1–N)
    types = relationship(
        "PokemonType",
        back_populates="pokemon",
        cascade="all, delete-orphan",
    )

    #: Learnable moves and learning methods (1–N)
    moves = relationship(
        "PokemonMove",
        back_populates="pokemon",
        cascade="all, delete-orphan",
    )

    form = relationship(
        "Form",
        back_populates="pokemons"
        )

    __table_args__ = (
        # Ensure only one given form exists per species
        UniqueConstraint(
            "species_id",
            "form_id",
            name="uq_species_form",
        ),
    )
