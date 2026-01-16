from api_client import get_pokemon_list, get_pokemon_detail
from formatters.pokemon_formatter import format_pokemon_selector
from formatters.move_formatter import format_pokemon_moves


def get_pokemon_options():
    """
    Return formatted Pokémon list for selector (Streamlit) as Pydantic objects.
    """
    pokemons_json = get_pokemon_list()
    return format_pokemon_selector(pokemons_json)


def get_moves_for_pokemon(
    pokemon_id: int,
    type_filter: str | None = None,
    category_filter: str | None = None,
    level_only: bool = False,
):
    """
    Return formatted moves for a Pokémon as Pydantic objects.
    """
    pokemon_json = get_pokemon_detail(pokemon_id)
    moves_json = pokemon_json.get("moves", []) if pokemon_json else []

    return format_pokemon_moves(
        moves_json,
        filter_type=type_filter,
        filter_category=category_filter,
        level_only=level_only,
    )
