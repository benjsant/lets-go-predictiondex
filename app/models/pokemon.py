# app/models/pokemon.py

from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    Numeric,
    Text,
    ForeignKey,
    UniqueConstraint,
    TIMESTAMP,
    func,
)
from sqlalchemy.orm import relationship
from app.db.base import Base


class Pokemon(Base):
    __tablename__ = "pokemon"

    id = Column(Integer, primary_key=True)

    species_id = Column(
        Integer,
        ForeignKey("pokemon_species.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Identifiants techniques (scraping / API / comparaisons)
    nom_pokeapi = Column(String(100), nullable=False, unique=True)
    nom_pokepedia = Column(String(150), nullable=False)

    # Nom lisible de la forme (Base, Mega X, Mega Y, Alola, etc.)
    form_name = Column(String(100), nullable=False)

    # Flags de forme
    is_mega = Column(Boolean, nullable=False, default=False)
    is_alola = Column(Boolean, nullable=False, default=False)
    is_starter = Column(Boolean, nullable=False, default=False)

    height_m = Column(Numeric(5, 2), nullable=False)
    weight_kg = Column(Numeric(5, 2), nullable=False)
    sprite_url = Column(Text)

    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    # Relations
    species = relationship(
        "PokemonSpecies",
        back_populates="pokemons",
    )

    stats = relationship(
        "PokemonStat",
        back_populates="pokemon",
        uselist=False,
        cascade="all, delete-orphan",
    )

    types = relationship(
        "PokemonType",
        back_populates="pokemon",
        cascade="all, delete-orphan",
    )

    moves = relationship(
        "PokemonMove",
        back_populates="pokemon",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        # Une seule forme donnée par espèce
        UniqueConstraint(
            "species_id",
            "form_name",
            name="uq_species_form",
        ),
    )
