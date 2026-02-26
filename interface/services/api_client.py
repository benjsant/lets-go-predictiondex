from typing import Dict, List, Optional

import requests

from interface.config.settings import API_BASE_URL, API_KEY


def _get_headers() -> dict:
    headers = {}
    if API_KEY:
        headers["X-API-Key"] = API_KEY
    return headers


def _get(endpoint: str, timeout: int = 30):
    try:
        url = f"{API_BASE_URL}{endpoint}"
        response = requests.get(url, headers=_get_headers(), timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API GET Error on {endpoint}: {e}")
        return None


def _post(endpoint: str, data: dict, timeout: int = 60):
    response = None
    try:
        url = f"{API_BASE_URL}{endpoint}"
        response = requests.post(url, json=data, headers=_get_headers(), timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API POST Error on {endpoint}: {e}")
        if response is not None and response.text:
            print(f"Response: {response.text}")
        return None


def get_all_pokemon() -> List[Dict]:
    return _get("/pokemon/")


def get_pokemon_by_id(pokemon_id: int) -> Dict:
    return _get(f"/pokemon/{pokemon_id}")


def get_pokemon_weaknesses(pokemon_id: int) -> List[Dict]:
    return _get(f"/pokemon/{pokemon_id}/weaknesses")


def search_pokemon(name: str) -> List[Dict]:
    return _get(f"/pokemon/search?name={name}")


def get_all_moves() -> List[Dict]:
    return _get("/moves/")


def get_move_by_id(move_id: int) -> Dict:
    return _get(f"/moves/id/{move_id}")


def get_moves_by_type(type_name: str) -> List[Dict]:
    return _get(f"/moves/by-type/{type_name}")


def search_moves(name: str) -> List[Dict]:
    return _get(f"/moves/search?name={name}")


def get_all_types() -> List[Dict]:
    return _get("/types/")


def get_type_affinities() -> List[Dict]:
    return _get("/types/affinities")


def get_type_affinities_by_name(attacking_type: str, defending_type: str) -> Dict:
    return _get(f"/types/affinities/by-name?attacking_type={attacking_type}&defending_type={defending_type}")


def get_pokemon_by_type(type_id: int) -> List[Dict]:
    return _get(f"/types/{type_id}/pokemon")


def get_pokemon_by_type_name(type_name: str) -> List[Dict]:
    return _get(f"/types/by-name/{type_name}/pokemon")


def predict_best_move(
    pokemon_a_id: int,
    pokemon_b_id: int,
    available_moves: List[str],
    available_moves_b: Optional[List[str]] = None
) -> Dict:
    """Predict the best move for Pokemon A against Pokemon B."""
    payload = {
        "pokemon_a_id": pokemon_a_id,
        "pokemon_b_id": pokemon_b_id,
        "available_moves": available_moves
    }

    if available_moves_b:
        payload["available_moves_b"] = available_moves_b

    return _post("/predict/best-move", payload)


def get_model_info() -> Dict:
    return _get("/predict/model-info")
