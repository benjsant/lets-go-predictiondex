# core/models/move.py
"""SQLAlchemy model for Pokemon moves."""

from sqlalchemy import Column, ForeignKey, Integer, String, Text
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

    #: Move priority (-7 to +2, default 0)
    #: +2: Protection moves (Abri)
    #: +1: Priority moves (Vive-Attaque, Aqua-Jet, Éclats Glace)
    #: 0: Normal moves
    #: -1: Charge moves (two-turn attacks)
    #: -5: Counter moves (Riposte, Voile Miroir)
    #: -7: Last moves (always move last)
    priority = Column(Integer, default=0, nullable=False)

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
