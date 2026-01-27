# core/models/pokemon_stat.py

"""
SQLAlchemy Model – PokemonStat
==============================

This module defines the `PokemonStat` model, which represents the **base
combat statistics** of a Pokémon in Pokémon Let's Go Pikachu / Eevee.

These statistics are intrinsic to a Pokémon form and are independent of:
- moves,
- learn methods,
- battle context.

Each Pokémon has **exactly one** associated stat line, enforced through a
one-to-one relationship using the Pokémon ID as the primary key.

Data is primarily sourced from PokéAPI.
"""

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from core.db.base import Base


class PokemonStat(Base):
    """
    Base combat statistics of a Pokémon.

    This table stores the canonical stat values used for:
    - damage calculation,
    - battle simulation,
    - feature generation for machine learning models.

    The primary key is shared with the Pokémon entity, ensuring a strict
    one-to-one relationship between a Pokémon and its stats.

    Stored statistics:
    - HP
    - Attack
    - Defense
    - Special Attack
    - Special Defense
    - Speed
    """

    __tablename__ = "pokemon_stat"

    #: Pokémon identifier (shared primary key, 1–1 relationship)
    pokemon_id = Column(
        Integer,
        ForeignKey("pokemon.id", ondelete="CASCADE"),
        primary_key=True,
    )

    #: Base HP stat
    hp = Column(Integer, nullable=False)

    #: Base Attack stat
    attack = Column(Integer, nullable=False)

    #: Base Defense stat
    defense = Column(Integer, nullable=False)

    #: Base Special Attack stat
    sp_attack = Column(Integer, nullable=False)

    #: Base Special Defense stat
    sp_defense = Column(Integer, nullable=False)

    #: Base Speed stat
    speed = Column(Integer, nullable=False)

    #: Relationship back to the Pokémon entity
    pokemon = relationship("Pokemon", back_populates="stats")
