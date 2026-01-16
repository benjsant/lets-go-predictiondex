# app/formatters/move_formatter.py

from typing import List, Dict, Optional
from formatters.ui.move_ui import MoveSelectItem

def format_pokemon_moves(
    moves: List[Dict],
    *,
    filter_type: Optional[str] = None,
    filter_category: Optional[str] = None,
    level_only: bool = False,
) -> List[MoveSelectItem]:
    """
    Convert moves JSON from API to Pydantic objects for Streamlit, with filters.
    """
    formatted: List[MoveSelectItem] = []

    for m in moves:
        if filter_type and m.get("type") != filter_type:
            continue
        if filter_category and m.get("category") != filter_category:
            continue
        if level_only and m.get("learn_method") != "level_up":
            continue

        label_parts = [
            m.get("name", ""),
            m.get("type", ""),
            m.get("category", ""),
        ]
        if m.get("learn_level") is not None:
            label_parts.append(f"lvl {m['learn_level']}")

        label = " – ".join(label_parts)

        formatted.append(
            MoveSelectItem(
                id=m.get("id"),
                name=m.get("name", ""),
                label=label,
                type=m.get("type", ""),
                category=m.get("category", ""),
                learn_method=m.get("learn_method"),
                learn_level=m.get("learn_level"),
            )
        )

    return formatted

