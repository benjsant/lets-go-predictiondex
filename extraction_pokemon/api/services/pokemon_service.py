# extraction_pokemon/api/services/pokemon_service.py

"""
Pokémon service layer
====================

Provides database access for Pokémon entities.

This service is responsible for:
- querying Pokémon data
- eager-loading all required relationships
- returning ORM objects ready for Pydantic serialization
"""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from extraction_pokemon.models import (
    Pokemon,
    PokemonType,
    Move,
    PokemonMove,
    TypeEffectiveness, 
    Type
)
from collections import defaultdict
from decimal import Decimal

# -------------------------
# 🔹 List Pokémon
# -------------------------
def list_pokemon(db: Session) -> List[Pokemon]:
    """
    Retrieve all Pokémon for list views.

    Eager-loaded relationships:
    - species
    - form
    - types (with type details)
    """
    return (
        db.query(Pokemon)
        .options(
            joinedload(Pokemon.species),
            joinedload(Pokemon.form),
            joinedload(Pokemon.types)
                .joinedload(PokemonType.type),
        )
        .order_by(Pokemon.id)
        .all()
    )


# -------------------------
# 🔹 Pokémon detail
# -------------------------
def get_pokemon_by_id(
    db: Session,
    pokemon_id: int,
) -> Optional[Pokemon]:
    """
    Retrieve a Pokémon by ID for detail view.

    Eager-loaded relationships:
    - species
    - form
    - base stats
    - types (with type details)
    - moves:
        - move
        - move type
        - move category
        - learn method
    """
    return (
        db.query(Pokemon)
        .options(
            joinedload(Pokemon.species),
            joinedload(Pokemon.form),
            joinedload(Pokemon.stats),
            joinedload(Pokemon.types)
                .joinedload(PokemonType.type),
            joinedload(Pokemon.moves)
                .joinedload(PokemonMove.move)
                .joinedload(Move.type),
            joinedload(Pokemon.moves)
                .joinedload(PokemonMove.move)
                .joinedload(Move.category),
            joinedload(Pokemon.moves)
                .joinedload(PokemonMove.learn_method),
        )
        .filter(Pokemon.id == pokemon_id)
        .one_or_none()
    )

# -------------------------
# 🔹 Search Pokémon by species name
# -------------------------
def search_pokemon_by_species_name(db: Session, name: str, lang: str = "fr") -> List[Pokemon]:
    """
    Search Pokémon by species name (localized).

    Parameters
    ----------
    name : str
        Partial or full name to search.
    lang : str
        Language code (default 'fr').

    Returns
    -------
    List[Pokemon]
    """
    species_name_field = getattr(Pokemon.species.property.mapper.class_, f"name_{lang}")
    return (
        db.query(Pokemon)
        .join(Pokemon.species)
        .filter(species_name_field.ilike(f"%{name}%"))
        .options(
            joinedload(Pokemon.form),
            joinedload(Pokemon.species),
            joinedload(Pokemon.types).joinedload(PokemonType.type),
        )
        .order_by(Pokemon.id)
        .all()
    )

def compute_pokemon_weaknesses(
    db: Session,
    pokemon_id: int,
):
    pokemon = (
        db.query(Pokemon)
        .filter(Pokemon.id == pokemon_id)
        .one_or_none()
    )

    if not pokemon:
        return None

    defending_type_ids = [pt.type_id for pt in pokemon.types]

    # Base multiplier = 1
    multipliers = defaultdict(lambda: Decimal("1.0"))

    # Toutes les relations où le Pokémon est défenseur
    affinities = (
        db.query(TypeEffectiveness)
        .filter(TypeEffectiveness.defending_type_id.in_(defending_type_ids))
        .all()
    )

    for eff in affinities:
        multipliers[eff.attacking_type_id] *= eff.multiplier

    # Mapping ID → nom de type
    types = {
        t.id: t.name
        for t in db.query(Type).all()
    }

    # On renvoie **tous les types**, même neutralité
    return [
        {
            "attacking_type": types[type_id],
            "multiplier": float(multiplier),
        }
        for type_id, multiplier in multipliers.items()
    ]
