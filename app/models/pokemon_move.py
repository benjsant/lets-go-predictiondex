# app/models/pokemon_move.py
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base


class PokemonMove(Base):
    __tablename__ = "pokemon_move"

    id = Column(Integer, primary_key=True)

    pokemon_id = Column(
        Integer,
        ForeignKey("pokemon.id", ondelete="CASCADE"),
        nullable=False,
    )
    move_id = Column(
        Integer,
        ForeignKey("move.id", ondelete="CASCADE"),
        nullable=False,
    )
    learn_method_id = Column(
        Integer,
        ForeignKey("learn_method.id"),
        nullable=False,
    )
    learn_level = Column(Integer)

    __table_args__ = (
        UniqueConstraint(
            "pokemon_id",
            "move_id",
            "learn_method_id",
            name="uq_pokemon_move_method",
        ),
    )

    pokemon = relationship("Pokemon", back_populates="moves")
    move = relationship("Move", back_populates="pokemons")
    learn_method = relationship("LearnMethod", back_populates="pokemon_moves")

