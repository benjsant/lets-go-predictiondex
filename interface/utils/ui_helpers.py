# interface/utils/ui_helpers.py

from typing import List, Optional

from interface.formatters.move_formatter import format_pokemon_moves
from interface.formatters.pokemon_formatter import format_pokemon_selector
from interface.formatters.ui.move_ui import MoveSelectItem
from interface.formatters.ui.pokemon_ui import PokemonSelectItem
from interface.services.move_service import get_types
from interface.services.pokemon_service import get_pokemon_detail, get_pokemon_list, get_pokemon_weaknesses


def get_pokemon_options(include_special_forms: bool = False, sort_by_form: bool = False) -> List[PokemonSelectItem]:
    """Fetch and format all Pokemon for Streamlit selectors."""
    pokemons_json = get_pokemon_list()

    if not include_special_forms:
        filtered_pokemons = []
        for pokemon in pokemons_json:
            name = pokemon.get("name", "").lower()
            if not any(keyword in name for keyword in ["alola", "mega", "giga", "galarian", "hisuian"]):
                filtered_pokemons.append(pokemon)
        pokemons_json = filtered_pokemons

    formatted_pokemons = format_pokemon_selector(pokemons_json)

    if sort_by_form:
        def get_sort_key(p: PokemonSelectItem):
            name_lower = p.name.lower()
            if "alola" in name_lower:
                return (1, p.name)
            elif "mega" in name_lower:
                return (2, p.name)
            elif "giga" in name_lower:
                return (3, p.name)
            return (0, p.name)
        formatted_pokemons = sorted(formatted_pokemons, key=get_sort_key)

    return formatted_pokemons


def get_pokemon_by_id(pokemon_id: int) -> Optional[PokemonSelectItem]:
    """Fetch a single Pokemon by ID."""
    pokemon_json = get_pokemon_detail(pokemon_id)
    if not pokemon_json:
        return None
    formatted = format_pokemon_selector([pokemon_json])
    return formatted[0] if formatted else None


def get_pokemon_weaknesses_ui(pokemon_id: int) -> List[dict]:
    """Fetch Pokemon weaknesses for UI display."""
    return get_pokemon_weaknesses(pokemon_id)


def get_moves_for_pokemon(
    pokemon_id: int,
    type_filter: Optional[str] = None,
    category_filter: Optional[str] = None,
    level_only: bool = False,
    unique: bool = False,
) -> List[MoveSelectItem]:
    """Fetch and filter Pokemon moves for Streamlit UI."""
    pokemon_json = get_pokemon_detail(pokemon_id)
    moves_json = pokemon_json.get("moves", []) if pokemon_json else []

    category_map = {"physique": "physical", "spécial": "special", "autre": "autre"}
    category_filter_normalized = category_map.get(category_filter.lower(), category_filter.lower()) if category_filter else None
    type_filter_normalized = type_filter.lower() if type_filter and type_filter != "Toutes" else None

    return format_pokemon_moves(
        moves_json,
        filter_type=type_filter_normalized,
        filter_category=category_filter_normalized,
        level_only=level_only,
        unique=unique,
    )


def get_type_options() -> List[str]:
    """Fetch type list for selectbox options."""
    types_json = get_types()
    return ["Toutes"] + [t.get("name") for t in types_json]
