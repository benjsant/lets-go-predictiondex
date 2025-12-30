# app/models/pokemon.py
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    Numeric,
    Text,
    TIMESTAMP,
    func,
)
from sqlalchemy.orm import relationship
from app.db.base import Base


class Pokemon(Base):
    __tablename__ = "pokemon"

    id = Column(Integer, primary_key=True)
    pokedex_number = Column(Integer, nullable=False)
    name_fr = Column(String(75), nullable=False)
    name_en = Column(String(75))  # utile pour le nom anglais
    is_alola = Column(Boolean, nullable=False, default=False)
    is_mega = Column(Boolean, nullable=False, default=False)
    height_m = Column(Numeric(5, 2), nullable=False)
    weight_kg = Column(Numeric(5, 2), nullable=False)
    sprite_url = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    stats = relationship("PokemonStat", back_populates="pokemon", uselist=False)
    types = relationship("PokemonType", back_populates="pokemon", cascade="all, delete-orphan")
    moves = relationship("PokemonMove", back_populates="pokemon", cascade="all, delete-orphan")
