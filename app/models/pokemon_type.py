# app/models/pokemon_type.py
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base


class PokemonType(Base):
    __tablename__ = "pokemon_type"

    pokemon_id = Column(Integer, ForeignKey("pokemon.id", ondelete="CASCADE"), primary_key=True)
    type_id = Column(Integer, ForeignKey("type.id"), nullable=False)
    slot = Column(Integer, primary_key=True)

    pokemon = relationship("Pokemon", back_populates="types")
    type = relationship("Type")

    __table_args__ = (UniqueConstraint("pokemon_id", "slot", name="uq_pokemon_slot"),)
