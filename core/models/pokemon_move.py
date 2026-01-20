# core/models/pokemon_move.py
"""
SQLAlchemy Model – PokemonMove
==============================

This module defines the `PokemonMove` model, which represents the
**learning relationship between a Pokémon and a move**
in Pokémon Let's Go Pikachu / Eevee.

It is an enriched many-to-many (N–N) association table linking:
- a Pokémon (`Pokemon`),
- a move (`Move`),
- a learning method (`LearnMethod`).

The learning level is optional and depends on the learning method used.

This model is populated exclusively by the Scrapy pipeline
`PokemonMovePipeline`, based on data scraped from Poképédia.

It is a core building block of the project:
- complete move history per Pokémon,
- foundation for battle simulation,
- feature generation for prediction models.
"""

from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from core.db.base import Base


class PokemonMove(Base):
    """
    Pokémon ↔ Move association with learning method.

    Each row indicates that a Pokémon can learn a given move
    through a specific learning method (level-up, TM, move tutor, etc.).

    The uniqueness constraint ensures that a move can be associated
    only once per Pokémon for a given learning method.

    Business rules for `learn_level`:
    - None  → move learned via TM or Move Tutor
    - -1    → move learned upon evolution
    - 0     → move known at level 1 (starting move)
    - > 0   → exact level at which the move is learned

    Example:
    ┌────┬────────────┬─────────┬───────────────┬─────────────┐
    │ id │ pokemon_id │ move_id │ learn_method  │ learn_level │
    ├────┼────────────┼─────────┼───────────────┼─────────────┤
    │ 42 │ 25         │ 85      │ level_up      │ 26          │
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
        # 🔒 Global uniqueness: Pokémon + move + learning method
        UniqueConstraint(
            "pokemon_id",
            "move_id",
            "learn_method_id",
            name="uq_pokemon_move_unique",
        ),

        # 🔐 Database-level guard on learning level validity
        CheckConstraint(
            "learn_level IS NULL OR learn_level >= -1",
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
