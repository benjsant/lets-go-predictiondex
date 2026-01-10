from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.models import (
    Pokemon,
    PokemonMove,
    Move,
    PokemonType,
)


# -------------------------
# 🔹 Liste Pokémon
# -------------------------
def list_pokemon(db: Session) -> List[Pokemon]:
    return (
        db.query(Pokemon)
        .options(
            joinedload(Pokemon.species),
            joinedload(Pokemon.types).joinedload(PokemonType.type),
        )
        .order_by(Pokemon.id)
        .all()
    )


# -------------------------
# 🔹 Détail Pokémon
# -------------------------
def get_pokemon_by_id(
    db: Session,
    pokemon_id: int,
) -> Optional[Pokemon]:
    return (
        db.query(Pokemon)
        .options(
            joinedload(Pokemon.species),
            joinedload(Pokemon.stats),
            joinedload(Pokemon.types).joinedload(PokemonType.type),
            joinedload(Pokemon.moves)
                .joinedload(PokemonMove.move)
                .joinedload(Move.type),
            joinedload(Pokemon.moves)
                .joinedload(PokemonMove.learn_method),
        )
        .filter(Pokemon.id == pokemon_id)
        .one_or_none()
    )
