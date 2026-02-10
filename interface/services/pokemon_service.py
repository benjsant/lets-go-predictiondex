# interface/services/pokemon_service.py

from .api_client import _get


def get_pokemon_list():
    """Récupère la liste de tous les Pokémon depuis l'API."""
    return _get("/pokemon/")


def get_pokemon_detail(pokemon_id: int):
    """Récupère le détail d'un Pokémon spécifique par ID."""
    return _get(f"/pokemon/{pokemon_id}")


def get_pokemon_weaknesses(pokemon_id: int):
    """
    Récupère les faiblesses (multiplicateurs de dégâts reçus) d'un Pokémon.

    Retourne une liste de dicts avec :
    - attacking_type : str
    - multiplier : float (conversion automatique)
    """
    weaknesses_json = _get(f"/pokemon/{pokemon_id}/weaknesses")

    if not weaknesses_json:
        return []

    # Sécurisation : conversion du multiplicateur en float
    for w in weaknesses_json:
        w["multiplier"] = float(w["multiplier"])

    return weaknesses_json
