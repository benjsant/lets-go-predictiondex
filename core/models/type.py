# core/models/type.py

"""
SQLAlchemy Model – Type
=======================

This module defines the `Type` model, representing an **elemental type**
in Pokémon Let's Go Pikachu / Eevee.

Each type is used to categorize:
- Pokémon (via `PokemonType`)
- Moves (via `Move`)
- Effectiveness calculations (via `TypeEffectiveness`)

This table is central to:
- battle mechanics (type advantages / disadvantages),
- damage calculations,
- feature engineering for ML simulations and predictions.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from core.db.base import Base


class Type(Base):
    """
    Elemental Pokémon type.

    Each row represents a distinct type (e.g., Fire, Water, Grass)
    and is linked to moves and Pokémon.

    Relationships:
    - `moves`: all moves of this type
    - `pokemon_types`: all Pokémon having this type (via PokemonType)

    Example:
    ┌────┬─────────┐
    │ id │ name    │
    ├────┼─────────┤
    │ 1  │ Fire    │
    │ 2  │ Water   │
    │ 3  │ Grass   │
    └────┴─────────┘
    """

    __tablename__ = "type"

    #: Unique type identifier
    id = Column(Integer, primary_key=True)

    #: Name of the type (Fire, Water, etc.)
    name = Column(String(50), nullable=False)

    #: Relationship to all moves of this type
    moves = relationship("Move", back_populates="type")
