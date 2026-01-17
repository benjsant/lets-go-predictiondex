# formatters/move_formatter.py

from typing import List, Dict, Optional
from interface.formatters.ui.move_ui import MoveSelectItem


def format_pokemon_moves(
    moves: List[Dict],
    filter_type: Optional[str] = None,
    filter_category: Optional[str] = None,
    level_only: bool = False,
) -> List[MoveSelectItem]:

    formatted = []

    for m in moves:
        if filter_type and m.get("type", {}).get("name") != filter_type:
            continue

        category = m.get("category", {}).get("name")
        if filter_category and category != filter_category:
            continue

        learn_method = m.get("learn_method", {}).get("name")
        learn_level = m.get("learn_level")

        if level_only and learn_method != "level-up":
            continue

        formatted.append(
            MoveSelectItem(
                id=m.get("id"),
                name=m.get("name"),
                label=f"{m.get('name')} ({category})",
                type=m.get("type", {}).get("name"),
                category=category,
                learn_method=learn_method,
                learn_level=learn_level,
            )
        )

    return formatted
