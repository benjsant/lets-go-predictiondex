# app/models/pokemon_move.py
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
)
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
        ForeignKey("learn_method.id", ondelete="CASCADE"),
        nullable=False,
    )

    # None = CT / Move tutor
    # -1 = Évolution
    # 0 = Départ
    # >0 = Niveau
    learn_level = Column(Integer, nullable=True)

    __table_args__ = (
        # 🔒 Guard DB GLOBAL
        UniqueConstraint(
            "pokemon_id",
            "move_id",
            "learn_method_id",
            name="uq_pokemon_move_unique",
        ),
        CheckConstraint(
            "learn_level IS NULL OR learn_level >= -1",
            name="ck_pokemon_move_learn_level",
        ),
    )

    pokemon = relationship("Pokemon", back_populates="moves")
    move = relationship("Move", back_populates="pokemons")
    learn_method = relationship("LearnMethod", back_populates="pokemon_moves")
