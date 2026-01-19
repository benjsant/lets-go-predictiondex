# interface/services/api_client.py

import requests
from interface.config.settings import API_BASE_URL


def _get(endpoint: str):
    url = f"{API_BASE_URL}{endpoint}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()
