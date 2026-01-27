# core/models/move_category.py

"""
SQLAlchemy Model – MoveCategory
===============================

Represents the category of a Pokémon move (Physical, Special, Status).
Used for normalization and referential integrity.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from core.db.base import Base


class MoveCategory(Base):
    """
    Pokémon Move Category entity.

    Centralizes all possible move categories and links to moves.
    """
    __tablename__ = "move_category"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)

    #: Relationship to moves
    moves = relationship("Move", back_populates="category")
