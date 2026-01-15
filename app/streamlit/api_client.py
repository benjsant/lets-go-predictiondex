import os
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://app:8000")


def get_pokemon_list():
    response = requests.get(f"{API_BASE_URL}/pokemon/")
    response.raise_for_status()
    return response.json()


def get_pokemon_detail(pokemon_id: int):
    response = requests.get(f"{API_BASE_URL}/pokemon/{pokemon_id}")
    response.raise_for_status()
    return response.json()


def get_types():
    response = requests.get(f"{API_BASE_URL}/types/")
    response.raise_for_status()
    return response.json()
