# app/formatters/move_formatter.py

from typing import List, Optional

from app.schemas.pokemon import PokemonMoveUIOut
from app.formatters.ui.move_ui import MoveSelectItem


def format_pokemon_moves(
    moves: List[PokemonMoveUIOut],
    *,
    filter_type: Optional[str] = None,
    filter_category: Optional[str] = None,
    level_only: bool = False,
) -> List[MoveSelectItem]:
    """
    Format and optionally filter Pokémon moves for UI (Streamlit).
    """
    formatted: List[MoveSelectItem] = []

    for m in moves:
        if filter_type and m.type != filter_type:
            continue

        if filter_category and m.category != filter_category:
            continue

        if level_only and m.learn_method != "level_up":
            continue

        parts = [
            m.name,
            m.type,
            m.category,
        ]

        if m.learn_level is not None:
            parts.append(f"lvl {m.learn_level}")

        label = " – ".join(parts)

        formatted.append(
            MoveSelectItem(
                name=m.name,
                label=label,
                type=m.type,
                category=m.category,
                learn_method=m.learn_method,
                learn_level=m.learn_level,
            )
        )

    return formatted
