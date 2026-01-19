# formatters/pokemon_formatter.py
from typing import List, Dict
from interface.formatters.ui.pokemon_ui import PokemonSelectItem

def format_pokemon_selector(pokemons: List[Dict]) -> List[PokemonSelectItem]:
    """
    Transforme la liste JSON de Pokémon en objets Streamlit exploitables.

    Chaque Pokémon contient :
    - Nom FR + forme (si autre que base)
    - Types
    - Stats et total_stats
    - Numéro Pokédex
    - Sprite URL
    - Taille et poids (facultatif)
    """

    formatted: List[PokemonSelectItem] = []

    for p in pokemons:
        # Sécurité minimale : ignorer les entrées mal formées
        if "id" not in p or "species" not in p:
            continue

        species = p.get("species", {})
        form = p.get("form", {})

        # Nom FR + forme
        name = species.get("name_fr", "Inconnu")
        form_name = form.get("name")
        if form_name and form_name.lower() != "base":
            name = f"{name} ({form_name})"

        # Types
        types = [t["name"] for t in p.get("types", []) if "name" in t]

        # Stats
        stats = p.get("stats", None)
        total_stats = sum(stats.values()) if stats else None

        # Numéro Pokédex
        pokedex_number = species.get("pokedex_number", None)

        # Taille et poids
        height_m = p.get("height_m", None)
        weight_kg = p.get("weight_kg", None)

        # Construction de l'objet Streamlit
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
