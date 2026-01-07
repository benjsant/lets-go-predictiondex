# app/models/pokemon_stat.py
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class PokemonStat(Base):
    __tablename__ = "pokemon_stat"

    pokemon_id = Column(
        Integer,
        ForeignKey("pokemon.id", ondelete="CASCADE"),
        primary_key=True,
    )

    hp = Column(Integer, nullable=False)
    attack = Column(Integer, nullable=False)
    defense = Column(Integer, nullable=False)
    sp_attack = Column(Integer, nullable=False)
    sp_defense = Column(Integer, nullable=False)
    speed = Column(Integer, nullable=False)

    pokemon = relationship("Pokemon", back_populates="stats")
