"""
Move formatters
===============

Format Pokémon moves for UI selection and filtering.
"""

from typing import List, Dict, Optional
from app.schemas.pokemon import PokemonMoveOut


def format_pokemon_moves(
    moves: List[PokemonMoveOut],
    *,
    filter_type: Optional[str] = None,
    filter_category: Optional[str] = None,
    level_only: bool = False,
) -> List[Dict]:
    """
    Format and optionally filter Pokémon moves for UI.

    Filters:
    - filter_type: only moves of this type
    - filter_category: Physique / Spécial / Statut
    - level_only: only level-up moves
    """
    formatted = []

    for m in moves:
        if filter_type and m.type != filter_type:
            continue

        if filter_category and m.category != filter_category:
            continue

        if level_only and m.learn_method != "level-up":
            continue

        parts = [m.name, f"{m.type}", f"{m.category}"]

        if m.learn_level is not None:
            parts.append(f"lvl {m.learn_level}")

        label = " – ".join(parts)

        formatted.append(
            {
                "name": m.name,
                "label": label,
                "type": m.type,
                "category": m.category,
                "learn_method": m.learn_method,
                "learn_level": m.learn_level,
            }
        )

    return formatted
