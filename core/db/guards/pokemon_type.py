from sqlalchemy.orm import Session

from core.models import PokemonType


def upsert_pokemon_type(
    session: Session,
    *,
    pokemon_id: int,
    type_id: int,
    slot: int,
) -> PokemonType:
    """Insert or update a type for a Pokemon with given slot (1=primary, 2=secondary)."""

    if slot not in (1, 2):
        raise ValueError("slot doit être 1 ou 2")

    pokemon_type = (
        session.query(PokemonType)
        .filter(
            PokemonType.pokemon_id == pokemon_id,
            PokemonType.slot == slot,
        )
        .one_or_none()
    )

    if pokemon_type:
        # Mise à jour du type pour ce slot
        pokemon_type.type_id = type_id
        return pokemon_type

    pokemon_type = PokemonType(
        pokemon_id=pokemon_id,
        type_id=type_id,
        slot=slot,
    )
    session.add(pokemon_type)
    return pokemon_type
