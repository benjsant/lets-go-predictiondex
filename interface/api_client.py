# app/interface/api_client.py
import os
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://api:8000")


def _get(url: str):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def get_pokemon_list():
    return _get(f"{API_BASE_URL}/pokemon/")


def get_pokemon_detail(pokemon_id: int):
    return _get(f"{API_BASE_URL}/pokemon/{pokemon_id}")


def get_types():
    return _get(f"{API_BASE_URL}/types/")

