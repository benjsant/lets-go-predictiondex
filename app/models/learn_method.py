# app/models/learn_method.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base


class LearnMethod(Base):
    __tablename__ = "learn_method"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)

    pokemon_moves = relationship("PokemonMove", back_populates="learn_method")
