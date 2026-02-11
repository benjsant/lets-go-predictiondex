"""SQLAlchemy model for Pokemon forms (Base, Mega, Alola, etc.)."""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from core.db.base import Base


class Form(Base):
    """
    Pokémon Form entity.

    Centralizes all form-specific properties:
    - Name of the form (Base, Mega, Alola, etc.)

    This allows multiple Pokémon to reference the same canonical form.
    """
    __tablename__ = "form"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)

    #: Relationship to Pokémon
    pokemons = relationship("Pokemon", back_populates="form")
