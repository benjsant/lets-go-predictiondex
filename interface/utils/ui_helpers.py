from interface.services.pokemon_service import (
    get_pokemon_list,
    get_pokemon_detail,
)
from interface.formatters.pokemon_formatter import format_pokemon_selector
from interface.formatters.move_formatter import format_pokemon_moves


def get_pokemon_options():
    pokemons_json = get_pokemon_list()
    return format_pokemon_selector(pokemons_json)


def get_moves_for_pokemon(
    pokemon_id: int,
    type_filter=None,
    category_filter=None,
    level_only=False,
):
    pokemon_json = get_pokemon_detail(pokemon_id)
    moves_json = pokemon_json.get("moves", []) if pokemon_json else []

    return format_pokemon_moves(
        moves_json,
        filter_type=type_filter,
        filter_category=category_filter,
        level_only=level_only,
    )
