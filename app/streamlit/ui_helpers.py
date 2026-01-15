from app.streamlit.api_client import (
    get_pokemon_list,
    get_pokemon_detail,
)
from app.formatters.pokemon_formatter import format_pokemon_selector
from app.formatters.move_formatter import format_pokemon_moves


def get_pokemon_options():
    """Return formatted Pokémon for selector."""
    pokemons = get_pokemon_list()
    return format_pokemon_selector(pokemons)


def get_moves_for_pokemon(
    pokemon_id: int,
    type_filter=None,
    category_filter=None,
    level_only=False,
):
    """Return formatted moves for a Pokémon."""
    pokemon = get_pokemon_detail(pokemon_id)
    if not pokemon:
        return []

    return format_pokemon_moves(
        pokemon["moves"],
        filter_type=type_filter,
        filter_category=category_filter,
        level_only=level_only,
    )
