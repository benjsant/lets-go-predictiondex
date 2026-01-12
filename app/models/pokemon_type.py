# app/models/pokemon_type.py

"""
SQLAlchemy Model – PokemonType
==============================

This module defines the `PokemonType` model, which represents the **elemental
typing of a Pokémon** in Pokémon Let's Go Pikachu / Eevee.

It is an enriched association table linking:
- a Pokémon (`Pokemon`),
- an elemental type (`Type`),
- a slot indicating primary or secondary typing.

Each Pokémon can have one or two types, ordered by slot:
- slot = 1 → primary type
- slot = 2 → secondary type
"""

from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base


class PokemonType(Base):
    """
    Association between a Pokémon and its elemental types.

    This table defines the typing of a Pokémon form, including the ordering
    of types via the `slot` field.

    Business rules:
    - A Pokémon can have at most two types.
    - Each slot (1 or 2) can only be used once per Pokémon.
    - Slot ordering is important for display and damage calculations.

    This model is used for:
    - type effectiveness computation,
    - battle simulation,
    - feature generation for machine learning models.
    """

    __tablename__ = "pokemon_type"

    #: Pokémon identifier
    pokemon_id = Column(
        Integer,
        ForeignKey("pokemon.id", ondelete="CASCADE"),
        primary_key=True,
    )

    #: Elemental type identifier
    type_id = Column(
        Integer,
        ForeignKey("type.id"),
        nullable=False,
    )

    #: Type slot (1 = primary, 2 = secondary)
    slot = Column(Integer, primary_key=True)

    #: Relationship back to the Pokémon entity
    pokemon = relationship("Pokemon", back_populates="types")

    #: Relationship to the elemental Type entity
    type = relationship("Type")
