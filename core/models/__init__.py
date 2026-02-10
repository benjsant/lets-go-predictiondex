"""
SQLAlchemy models package
=========================

This package aggregates all SQLAlchemy ORM models used by the
Pokémon Let's Go project.

Importing this module ensures that:
- All ORM models are registered in SQLAlchemy metadata
- Table relationships are properly resolved
- Alembic or schema initialization tools can detect all models

This file does not contain business logic and should only expose
model classes.
"""

# Third-party / shared imports
from core.db.base import Base

from .form import Form
from .learn_method import LearnMethod
from .move import Move
from .move_category import MoveCategory
from .pokemon import Pokemon
from .pokemon_move import PokemonMove

# Local model imports (order matters for relationships)
from .pokemon_species import PokemonSpecies
from .pokemon_stat import PokemonStat
from .pokemon_type import PokemonType
from .type import Type
from .type_effectiveness import TypeEffectiveness

__all__ = [
    "Base",
    "PokemonSpecies",
    "Pokemon",
    "PokemonStat",
    "PokemonType",
    "Type",
    "Move",
    "PokemonMove",
    "LearnMethod",
    "TypeEffectiveness",
    "Form",
    "MoveCategory"
]
