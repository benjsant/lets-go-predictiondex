# app/models/move.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Move(Base):
    __tablename__ = "move"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    power = Column(Integer)
    accuracy = Column(Integer)
    description = Column(Text)
    category = Column(String(20), nullable=False)
    damage_type = Column(String(30))
    type_id = Column(Integer, ForeignKey("type.id"), nullable=False)

    type = relationship("Type", back_populates="moves")
    pokemons = relationship("PokemonMove", back_populates="move", cascade="all, delete-orphan")
