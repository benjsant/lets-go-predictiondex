# core/models/pokemon_move.py
"""SQLAlchemy model for Pokemon-Move learning associations."""

from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from core.db.base import Base


class PokemonMove(Base):
    """
    Pokémon ↔ Move association with learning method.

    Each row indicates that a Pokémon can learn a given move
    through a specific learning method (level-up, TM, move tutor, etc.).

    The uniqueness constraint a move can be associated
    only once per Pokémon for a given learning method.

    Business rules for `learn_level`:
    - None → move learned via TM or Move Tutor
    - -1 → move learned upon evolution
    - 0 → move known at level 1 (starting move)
    - > 0 → exact level at which the move is learned

    Example:
    ┌────┬────────────┬─────────┬───────────────┬─────────────┐
    │ id │ pokemon_id │ move_id │ learn_method │ learn_level │
    ├────┼────────────┼─────────┼───────────────┼─────────────┤
    │ 42 │ 25 │ 85 │ level_up │ 26 │
    └────┴────────────┴─────────┴───────────────┴─────────────┘
    """

    __tablename__ = "pokemon_move"

    #: Technical identifier of the association
    id = Column(Integer, primary_key=True)

    #: Pokémon that learns the move
    pokemon_id = Column(
        Integer,
        ForeignKey("pokemon.id", ondelete="CASCADE"),
        nullable=False,
    )

    #: Learned move
    move_id = Column(
        Integer,
        ForeignKey("move.id", ondelete="CASCADE"),
        nullable=False,
    )

    #: Learning method (level_up, ct, move_tutor, etc.)
    learn_method_id = Column(
        Integer,
        ForeignKey("learn_method.id", ondelete="CASCADE"),
        nullable=False,
    )

    #: Learning level (depends on the learning method)
    learn_level = Column(Integer, nullable=True)

    __table_args__ = (
        # Global uniqueness: Pokémon + move + learning method
        UniqueConstraint(
            "pokemon_id",
            "move_id",
            "learn_method_id",
            name="uq_pokemon_move_unique",
        ),

        # Database-level guard on learning level validity
        CheckConstraint(
            "learn_level IS NULL OR learn_level >= -2",
            name="ck_pokemon_move_learn_level",
        ),
    )

    #: Relationship to Pokémon
    pokemon = relationship("Pokemon", back_populates="moves")

    #: Relationship to move
    move = relationship("Move", back_populates="pokemons")

    #: Relationship to learning method
    learn_method = relationship(
        "LearnMethod",
        back_populates="pokemon_moves",
    )
