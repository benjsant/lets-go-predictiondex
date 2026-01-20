# core/schemas/type.py
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
