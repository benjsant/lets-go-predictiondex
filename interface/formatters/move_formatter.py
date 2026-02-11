# formatters/move_formatter.py
from typing import Dict, List, Optional

from interface.formatters.ui.move_ui import MoveSelectItem


def format_pokemon_moves(
    moves: List[Dict],
    filter_type: Optional[str] = None,
    filter_category: Optional[str] = None,
    level_only: bool = False,
    unique: bool = False,
) -> List[MoveSelectItem]:
    """Convert Pokemon move dicts into MoveSelectItem objects for Streamlit UI.
    
    Args:
        moves: List of move dictionaries from API
        filter_type: Filter by type name
        filter_category: Filter by category
        level_only: Only include level-up moves
        unique: Deduplicate moves by name (keeps first occurrence after sorting)
    """

    formatted: List[MoveSelectItem] = []

    for m in moves:
        # Skip incomplete entries
        name = m.get("name")
        move_type = m.get("type")
        category = m.get("category")

        if not name or not move_type or not category:
            continue

        # Apply filters
        if filter_type and move_type.lower() != filter_type.lower():
            continue

        if filter_category and category.lower() != filter_category.lower():
            continue

        learn_method = m.get("learn_method")
        learn_level = m.get("learn_level")

        if level_only and learn_method != "level_up":
            continue

        # Optional fields
        power = m.get("power")
        accuracy = m.get("accuracy")
        damage_type = m.get("damage_type")

        # Build display label
        label_parts = [name, f"({move_type} / {category})"]

        if learn_method == "level_up":
            if learn_level == 0:
                label_parts.append("Départ")
            elif learn_level == -2:
                label_parts.append("Hérité")
            elif learn_level is not None:
                label_parts.append(f"lvl {learn_level}")
        elif learn_method == "before_evolution":
            label_parts.append("Hérité")
        else:
            # CT / Tutor / Other learn methods
            label_parts.append(learn_method.upper() if learn_method else "AUTRE")

        label = " — ".join(label_parts)

        formatted.append(
            MoveSelectItem(
                name=name,
                label=label,
                type=move_type,
                category=category,
                learn_method=learn_method,
                learn_level=learn_level,
                power=power,
                accuracy=accuracy,
                damage_type=damage_type,
            )
        )

    # Sort by learn method priority, then level, then name
    priority = {"level_up": 0, "before_evolution": 1, "ct": 2, "move_tutor": 3}

    formatted.sort(
        key=lambda m: (
            priority.get(m.learn_method, 99),
            m.learn_level if m.learn_level is not None else 999,
            m.name,
        )
    )

    # Deduplicate by name if requested (keeps first occurrence = best learn method)
    if unique:
        seen_names = set()
        unique_moves = []
        for m in formatted:
            if m.name not in seen_names:
                seen_names.add(m.name)
                unique_moves.append(m)
        formatted = unique_moves

    return formatted
