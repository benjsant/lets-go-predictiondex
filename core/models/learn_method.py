# core/models/learn_method.py
"""SQLAlchemy model for move learning methods."""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from core.db.base import Base


class LearnMethod(Base):
    """
    Pokémon move learning method.

    This table describes **how** a move is learned by a Pokémon,
    independently of the Pokémon itself or the move definition.

    It is linked to the `pokemon_move` table through a one-to-many
    relationship.

    Key role in the project:
    - acts as a reference (lookup) table,
    - loaded into memory cache when Scrapy pipelines start,
    - guarantees strict consistency between scraped data and the database.

    Example rows:
    ┌────┬──────────────────┐
    │ id │ name │
    ├────┼──────────────────┤
    │ 1 │ level_up │
    │ 2 │ ct │
    │ 3 │ move_tutor │
    └────┴──────────────────┘
    """

    __tablename__ = "learn_method"

    #: Unique identifier of the learning method
    id = Column(Integer, primary_key=True)

    #: Normalized method name (unique, used by pipelines and spiders)
    name = Column(String(50), nullable=False, unique=True)
    # e.g.: level_up, ct, move_tutor, starter_exclusive, mega_exclusive

    #: Relationship to Pokémon move associations
    pokemon_moves = relationship(
        "PokemonMove",
        back_populates="learn_method",
    )
