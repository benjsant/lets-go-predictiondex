# app/formatters/pokemon_formatter.py

from typing import List
from app.schemas.pokemon import PokemonListItem
from app.formatters.ui.pokemon_ui import PokemonSelectItem


def format_pokemon_selector(
    pokemons: List[PokemonListItem],
) -> List[PokemonSelectItem]:
    """
    Format Pokémon list for UI selectors (Streamlit).
    """
    formatted: List[PokemonSelectItem] = []

    for p in pokemons:
        name = p.species.name
        if p.form and p.form.name.lower() != "base":
            name = f"{name} ({p.form.name})"

        formatted.append(
            PokemonSelectItem(
                id=p.id,
                name=name,
                sprite_url=p.sprite_url,
            )
        )

    return formatted
