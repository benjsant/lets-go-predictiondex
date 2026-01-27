# interface/services/api_client.py

from typing import Dict, List, Optional

import requests

from interface.config.settings import API_BASE_URL, API_KEY


def _get_headers() -> dict:
    """Get headers with API Key if configured."""
    headers = {}
    if API_KEY:
        headers["X-API-Key"] = API_KEY
    return headers


def _get(endpoint: str, timeout: int = 30):
    """Generic GET request."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        response = requests.get(url, headers=_get_headers(), timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ API GET Error on {endpoint}: {e}")
        return None


def _post(endpoint: str, data: dict, timeout: int = 60):
    """Generic POST request (higher timeout for ML predictions)."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        response = requests.post(url, json=data, headers=_get_headers(), timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ API POST Error on {endpoint}: {e}")
        if response.text:
            print(f"Response: {response.text}")
        return None


# ===== POKEMON ENDPOINTS =====

def get_all_pokemon() -> List[Dict]:
    """Get all Pokemon."""
    return _get("/pokemon/")


def get_pokemon_by_id(pokemon_id: int) -> Dict:
    """Get Pokemon details by ID."""
    return _get(f"/pokemon/{pokemon_id}")


def get_pokemon_weaknesses(pokemon_id: int) -> List[Dict]:
    """Get Pokemon weaknesses."""
    return _get(f"/pokemon/{pokemon_id}/weaknesses")


def search_pokemon(name: str) -> List[Dict]:
    """Search Pokemon by name."""
    return _get(f"/pokemon/search?name={name}")


# ===== MOVES ENDPOINTS =====

def get_all_moves() -> List[Dict]:
    """Get all moves."""
    return _get("/moves/")


def get_move_by_id(move_id: int) -> Dict:
    """Get move details by ID."""
    return _get(f"/moves/id/{move_id}")


def get_moves_by_type(type_name: str) -> List[Dict]:
    """Get moves by type."""
    return _get(f"/moves/by-type/{type_name}")


def search_moves(name: str) -> List[Dict]:
    """Search moves by name."""
    return _get(f"/moves/search?name={name}")


# ===== TYPES ENDPOINTS =====

def get_all_types() -> List[Dict]:
    """Get all types."""
    return _get("/types/")


def get_type_affinities() -> List[Dict]:
    """Get all type affinities (type effectiveness matrix)."""
    return _get("/types/affinities")


def get_type_affinities_by_name(attacking_type: str, defending_type: str) -> Dict:
    """Get type affinity for specific attacking/defending combination."""
    return _get(f"/types/affinities/by-name?attacking_type={attacking_type}&defending_type={defending_type}")


def get_pokemon_by_type(type_id: int) -> List[Dict]:
    """Get all Pokemon of a specific type."""
    return _get(f"/types/{type_id}/pokemon")


def get_pokemon_by_type_name(type_name: str) -> List[Dict]:
    """Get all Pokemon of a specific type by name."""
    return _get(f"/types/by-name/{type_name}/pokemon")


# ===== PREDICTION ENDPOINTS =====

def predict_best_move(
    pokemon_a_id: int,
    pokemon_b_id: int,
    available_moves: List[str],
    available_moves_b: Optional[List[str]] = None
) -> Dict:
    """
    Predict the best move for Pokemon A against Pokemon B.

    Args:
        pokemon_a_id: Your Pokemon ID
        pokemon_b_id: Opponent Pokemon ID
        available_moves: Your available move names
        available_moves_b: Opponent's available moves (optional, defaults to all)

    Returns:
        {
            "recommended_move": str,
            "win_probability": float,
            "all_moves": List[{move_name, win_probability, ...}]
        }
    """
    payload = {
        "pokemon_a_id": pokemon_a_id,
        "pokemon_b_id": pokemon_b_id,
        "available_moves": available_moves
    }

    if available_moves_b:
        payload["available_moves_b"] = available_moves_b

    return _post("/predict/best-move", payload)


def get_model_info() -> Dict:
    """Get ML model information and metrics."""
    return _get("/predict/model-info")
