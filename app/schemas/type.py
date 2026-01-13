#app/schemas/type.py
"""
Pydantic schemas – Pokémon types (optimisé)
===========================================

Ce module définit les schemas Pydantic pour exposer les types Pokémon via l'API.
Il est aligné avec les modèles SQLAlchemy et inclut les relations nécessaires pour
les moves et les slots dans le contexte Pokémon.
"""

from pydantic import BaseModel, ConfigDict
from typing import List


# -------------------------
# 🔹 Type Pokémon de base
# -------------------------
class TypeOut(BaseModel):
    """
    Schema de sortie pour un type Pokémon élémentaire.

    Ce schema est utilisé dans :
    - les listes de Pokémon,
    - les descriptions de moves,
    - les réponses API légères.
    """

    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# 🔹 Type Pokémon avec moves
# -------------------------
class TypeWithMoves(TypeOut):
    """
    Schema étendu incluant les moves associés à ce type.

    Aligné avec le modèle SQLAlchemy `Move.type_id`.
    Fournit une liste d'identifiants de moves pour les endpoints analytiques ou détaillés.
    """

    move_ids: List[int] = []

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# 🔹 Type d'un Pokémon avec slot
# -------------------------
class PokemonTypeOut(BaseModel):
    """
    Représente le type d'un Pokémon avec son slot (1 ou 2).

    Aligné avec le modèle SQLAlchemy `PokemonType`.
    """

    id: int  # identifiant du type
    name: str  # nom du type
    slot: int  # slot du type pour le Pokémon (1=primaire, 2=secondaire)

    model_config = ConfigDict(from_attributes=True)
