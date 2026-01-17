from .api_client import _get


def get_pokemon_list():
    return _get("/pokemon/")


def get_pokemon_detail(pokemon_id: int):
    return _get(f"/pokemon/{pokemon_id}")
