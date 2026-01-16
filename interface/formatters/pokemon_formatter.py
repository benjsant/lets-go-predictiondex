# app/formatters/pokemon_formatter.py

from typing import List, Dict
from formatters.ui.pokemon_ui import PokemonSelectItem

def format_pokemon_selector(pokemons: List[Dict]) -> List[PokemonSelectItem]:
    """
    Convert Pokémon JSON from API to Pydantic objects for Streamlit.
    """
    formatted: List[PokemonSelectItem] = []

    for p in pokemons:
        # Name + Form
        name = p.get("species", {}).get("name", "")
        form = p.get("form", {}).get("name") if p.get("form") else None
        if form and form.lower() != "base":
            name = f"{name} ({form})"

        types = [t.get("name", "") for t in p.get("types", [])] if p.get("types") else []

        formatted.append(
            PokemonSelectItem(
                id=p.get("id"),
                name=name,
                sprite_url=p.get("sprite_url"),
                types=types
            )
        )

    return formatted
