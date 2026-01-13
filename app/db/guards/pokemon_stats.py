#app/db/guards/pokemon_stats.py
from sqlalchemy.orm import Session
from app.models import PokemonStat
from .utils import commit_if_needed


def upsert_pokemon_stats(
    session: Session,
    *,
    pokemon_id: int,
    hp: int,
    attack: int,
    defense: int,
    sp_attack: int,
    sp_defense: int,
    speed: int,
    auto_commit: bool = False,
) -> PokemonStat:
    """
    Insert or update base stats for a Pokémon.

    Pokémon stats are enrichment data coming from external sources
    (PokeAPI). They may be created or updated safely.
    """

    stats = (
        session.query(PokemonStat)
        .filter(PokemonStat.pokemon_id == pokemon_id)
        .one_or_none()
    )

    if not stats:
        stats = PokemonStat(pokemon_id=pokemon_id)
        session.add(stats)

    stats.hp = hp
    stats.attack = attack
    stats.defense = defense
    stats.sp_attack = sp_attack
    stats.sp_defense = sp_defense
    stats.speed = speed

    commit_if_needed(session, auto_commit)
    return stats
