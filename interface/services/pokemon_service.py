# interface/services/pokemon_service.py

from .api_client import _get


def get_pokemon_list():
    """Fetch all Pokemon from API."""
    return _get("/pokemon/")


def get_pokemon_detail(pokemon_id: int):
    """Fetch Pokemon details by ID."""
    return _get(f"/pokemon/{pokemon_id}")


def get_pokemon_weaknesses(pokemon_id: int):
    """Fetch Pokemon type weaknesses (damage multipliers)."""
    weaknesses_json = _get(f"/pokemon/{pokemon_id}/weaknesses")
    for w in weaknesses_json:
        w["multiplier"] = float(w["multiplier"])
    return weaknesses_json
