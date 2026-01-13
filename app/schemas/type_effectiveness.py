#app/schemas/type_effectiveness.py
"""
Pydantic schema – Type effectiveness
===================================

Ce module définit les schemas Pydantic exposant l'efficacité des types Pokémon.

L'efficacité d'un type représente le multiplicateur de dégâts appliqué lorsqu'un
move d'un type attaquant touche un Pokémon d'un type défenseur.

Alignement SQLAlchemy :
- Table : type_effectiveness
- FK : attacking_type_id -> type.id
- FK : defending_type_id -> type.id
"""

from pydantic import BaseModel, ConfigDict
from decimal import Decimal


# -------------------------
# 🔹 Type effectiveness (brut)
# -------------------------
class TypeEffectivenessOut(BaseModel):
    """
    Schema de sortie représentant une relation d'efficacité de type.

    Exemple :
    - attacking = Plante
    - defending = Sol
    - multiplier = 2.00
    """

    attacking_type_id: int
    defending_type_id: int
    multiplier: Decimal

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# 🔹 Type effectiveness enrichi (lisible API)
# -------------------------
class TypeEffectivenessDetailedOut(BaseModel):
    """
    Schema enrichi exposant les noms des types au lieu des seuls IDs.

    Ce schema est idéal pour :
    - endpoints pédagogiques,
    - API publiques,
    - debugging,
    - affichage frontend.
    """

    attacking_type: str
    defending_type: str
    multiplier: Decimal

    model_config = ConfigDict(from_attributes=True)
