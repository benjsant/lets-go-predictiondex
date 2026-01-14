"""
Pokémon formatters
==================

Formatting utilities for UI (Streamlit) and ML pipelines.
Framework-agnostic: no FastAPI, no SQLAlchemy.
"""

from typing import List, Dict

from app.schemas.pokemon import PokemonListItem


def format_pokemon_selector(
    pokemons: List[PokemonListItem],
) -> List[Dict]:
    """
    Format Pokémon list for UI selectors.

    Output example:
    [
        {
            "id": 25,
            "label": "Pikachu (Électrik)",
            "types": ["Électrik"],
            "sprite_url": "..."
        }
    ]
    """
    formatted = []

    for p in pokemons:
        type_names = [t.name for t in p.types]

        label = p.species.name
        if p.form and p.form.name.lower() != "base":
            label = f"{label} ({p.form.name})"

        formatted.append(
            {
                "id": p.id,
                "label": label,
                "types": type_names,
                "sprite_url": p.sprite_url,
            }
        )

    return formatted
