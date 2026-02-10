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
def get_pokemon_options(include_special_forms: bool = False, sort_by_form: bool = False) -> List[PokemonSelectItem]:
    """
    Récupère la liste de tous les Pokémon depuis l'API et les formate
    pour Streamlit (nom, sprite, types, stats).

    Args:
        include_special_forms: Si False, exclut les formes Alola, Mega, etc.
        sort_by_form: Si True, trie les Pokémon par forme avant le nom
    """
    pokemons_json = get_pokemon_list()

    # Filtrer les formes spéciales si demandé
    if not include_special_forms:
        filtered_pokemons = []
        for pokemon in pokemons_json:
            name = pokemon.get("name", "").lower()
            # Exclure les formes Alola, Mega, Gigamax, etc.
            if not any(keyword in name for keyword in ["alola", "mega", "giga", "galarian", "hisuian"]):
                filtered_pokemons.append(pokemon)
        pokemons_json = filtered_pokemons

    formatted_pokemons = format_pokemon_selector(pokemons_json)

    # Trier par forme si demandé
    if sort_by_form:
        # Extraction de la forme depuis le nom (si présente)
        def get_sort_key(p: PokemonSelectItem):
            name_lower = p.name.lower()
            if "alola" in name_lower:
                return (1, p.name)  # Formes Alola après
            if "mega" in name_lower:
                return (2, p.name)  # Formes Mega après
            if "giga" in name_lower:
                return (3, p.name)  # Formes Gigamax après
            return (0, p.name)  # Formes normales en premier

        formatted_pokemons = sorted(formatted_pokemons, key=get_sort_key)

    return formatted_pokemons


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
