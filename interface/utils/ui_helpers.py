# interface/utils/ui_helpers.py

from typing import List, Optional

from interface.formatters.move_formatter import format_pokemon_moves
from interface.formatters.pokemon_formatter import format_pokemon_selector
from interface.formatters.ui.move_ui import MoveSelectItem
from interface.formatters.ui.pokemon_ui import PokemonSelectItem
from interface.services.move_service import get_types
from interface.services.pokemon_service import get_pokemon_detail, get_pokemon_list, get_pokemon_weaknesses


# -----------------------------
# Pokémon helpers
# -----------------------------
def get_pokemon_options() -> List[PokemonSelectItem]:
    """
    Récupère la liste de tous les Pokémon depuis l'API et les formate
    pour Streamlit (nom, sprite, types, stats).
    """
    pokemons_json = get_pokemon_list()
    return format_pokemon_selector(pokemons_json)


def get_pokemon_by_id(pokemon_id: int) -> Optional[PokemonSelectItem]:
    """
    Récupère un Pokémon spécifique par ID et le formate.
    """
    pokemon_json = get_pokemon_detail(pokemon_id)
    if not pokemon_json:
        return None
    formatted = format_pokemon_selector([pokemon_json])
    return formatted[0] if formatted else None


def get_pokemon_weaknesses_ui(pokemon_id: int) -> List[dict]:
    """
    Wrapper pour récupérer les faiblesses d'un Pokémon, prêt pour affichage UI.
    """
    return get_pokemon_weaknesses(pokemon_id)


# -----------------------------
# Moves helpers
# -----------------------------
def get_moves_for_pokemon(
    pokemon_id: int,
    type_filter: Optional[str] = None,
    category_filter: Optional[str] = None,
    level_only: bool = False,
) -> List[MoveSelectItem]:
    """
    Récupère les moves d'un Pokémon depuis l'API et les filtre selon :
    - type
    - catégorie
    - level-up uniquement
    Retourne une liste de MoveSelectItem pour Streamlit.
    """

    # Récupérer les données complètes du Pokémon
    pokemon_json = get_pokemon_detail(pokemon_id)
    moves_json = pokemon_json.get("moves", []) if pokemon_json else []

    # Normalisation catégorie pour compatibilité avec API
    category_map = {
        "physique": "physical",
        "spécial": "special",
        "autre": "autre"
    }
    if category_filter:
        category_filter_normalized = category_map.get(category_filter.lower(), category_filter.lower())
    else:
        category_filter_normalized = None

    # Normalisation type pour compatibilité avec API
    type_filter_normalized = type_filter.lower() if type_filter and type_filter != "Toutes" else None

    # Formatter les moves avec filtres
    return format_pokemon_moves(
        moves_json,
        filter_type=type_filter_normalized,
        filter_category=category_filter_normalized,
        level_only=level_only,
    )


# -----------------------------
# Types helpers
# -----------------------------
def get_type_options() -> List[str]:
    """
    Récupère la liste des types depuis l'API pour les selectbox.
    """
    types_json = get_types()
    return ["Toutes"] + [t.get("name") for t in types_json]
