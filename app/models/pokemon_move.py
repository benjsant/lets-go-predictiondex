# app/models/pokemon_move.py
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class PokemonMove(Base):
    __tablename__ = "pokemon_move"

    pokemon_id = Column(Integer, ForeignKey("pokemon.id", ondelete="CASCADE"), primary_key=True)
    move_id = Column(Integer, ForeignKey("move.id", ondelete="CASCADE"), primary_key=True)
    learn_method_id = Column(Integer, ForeignKey("learn_method.id"), nullable=False)
    learn_level = Column(Integer)

    pokemon = relationship("Pokemon", back_populates="moves")
    move = relationship("Move", back_populates="pokemons")
    learn_method = relationship("LearnMethod", back_populates="pokemon_moves")
