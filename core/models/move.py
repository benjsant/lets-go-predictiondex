# core/models/move.py
"""
SQLAlchemy Model – Move
======================

This module defines the `Move` model, representing a **Pokémon move**
in Pokémon Let's Go Pikachu / Eevee.

A move is defined independently of:
- the Pokémon that can learn it,
- the learning method,
- the learning level.

Those relationships are managed through the `pokemon_move` association table.

This model is primarily populated from:
- Poképédia (scraped descriptive data),
- PokéAPI (optional enrichment: power, accuracy, type, etc.).

It is a central entity of the project, used for:
- battle analysis,
- combat simulation,
- machine learning model training.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from core.db.base import Base


class Move(Base):
    """
    Pokémon move (attack or active ability).

    This table stores the **intrinsic characteristics** of a move,
    independently of how it is learned or which Pokémon can use it.

    It is linked to:
    - the elemental type (`Type`),
    - Pokémon through the `PokemonMove` association table.

    Business role:
    - single source of truth for moves,
    - foundation for damage calculation logic,
    - core feature entity for machine learning pipelines.

    """

    __tablename__ = "move"

    #: Unique identifier of the move
    id = Column(Integer, primary_key=True)

    #: Move name (normalized in ingestion pipelines)
    name = Column(String(100), nullable=False)

    #: Base power of the move (None for non-damaging moves)
    power = Column(Integer)

    #: Accuracy percentage (None if not applicable)
    accuracy = Column(Integer)

    #: Textual description of the move effect
    description = Column(Text)

    #: Foreign key to MoveCategory
    category_id = Column(Integer, ForeignKey("move_category.id"), nullable=False)
    category = relationship("MoveCategory", back_populates="moves")

    #: Damage subtype or special behavior (optional)
    damage_type = Column(String(50))

    #: Foreign key to the elemental type
    type_id = Column(Integer, ForeignKey("type.id"), nullable=False)
    
    #: Relationship to the elemental type
    type = relationship("Type", back_populates="moves")

    #: Many-to-many relationship with Pokémon via PokemonMove
    pokemons = relationship(
        "PokemonMove",
        back_populates="move",
        cascade="all, delete-orphan",
    )