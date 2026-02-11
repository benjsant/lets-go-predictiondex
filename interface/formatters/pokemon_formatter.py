# formatters/pokemon_formatter.py
from typing import Dict, List

from interface.formatters.ui.pokemon_ui import PokemonSelectItem


def format_pokemon_selector(pokemons: List[Dict]) -> List[PokemonSelectItem]:
    """Convert API Pokemon JSON list into PokemonSelectItem objects for Streamlit."""

    formatted: List[PokemonSelectItem] = []

    for p in pokemons:
        # Skip malformed entries
        if "id" not in p or "species" not in p:
            continue

        species = p.get("species", {})
        p.get("form", {})

        name = species.get("name_fr", "Inconnu")
        types = [t["name"] for t in p.get("types", []) if "name" in t]
        stats = p.get("stats", None)
        total_stats = sum(stats.values()) if stats else None
        pokedex_number = species.get("pokedex_number", None)
        height_m = p.get("height_m", None)
        weight_kg = p.get("weight_kg", None)
        formatted.append(
            PokemonSelectItem(
                id=p["id"],
                name=name,
                pokedex_number=pokedex_number,
                stats=stats,
                total_stats=total_stats,
                sprite_url=p.get("sprite_url"),
                types=types,
                height_m=height_m,
                weight_kg=weight_kg
            )
        )

    return formatted
