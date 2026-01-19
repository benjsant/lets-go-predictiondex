# /interface/formatters/ui/pokemon_ui.py

from pydantic import BaseModel
from typing import Optional, List, Dict

class PokemonSelectItem(BaseModel):
    """
    Modèle Pydantic pour la sélection de Pokémon dans Streamlit.
    Contient toutes les informations nécessaires pour l'affichage
    et éventuellement le ML.
    """
    id: int
    name: str
    pokedex_number: Optional[int] = None   # Numéro Pokédex
    sprite_url: Optional[str] = None       # URL du sprite
    types: List[str] = []                  # Types Pokémon
    stats: Optional[Dict[str, int]] = None # hp, attack, defense, sp_attack, sp_defense, speed
    total_stats: Optional[int] = None      # Somme de toutes les stats
    height_m: Optional[str] = None         # Taille en m
    weight_kg: Optional[str] = None        # Poids en kg
