# formatters/pokemon_formatter.py

from typing import List, Dict
from interface.formatters.ui.pokemon_ui import PokemonSelectItem


def format_pokemon_selector(pokemons: List[Dict]) -> List[PokemonSelectItem]:
    formatted = []

    for p in pokemons:
        name = p.get("species", {}).get("name", "")
        form = p.get("form", {}).get("name") if p.get("form") else None
        if form and form.lower() != "base":
            name = f"{name} ({form})"

        types = [t.get("name", "") for t in p.get("types", [])]

        formatted.append(
            PokemonSelectItem(
                id=p.get("id"),
                name=name,
                sprite_url=p.get("sprite_url"),
                types=types,
            )
        )

    return formatted

