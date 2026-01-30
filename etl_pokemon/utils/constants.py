"""
ETL Constants and Mappings
===========================

Centralized constants for ETL processes.
"""

from typing import Optional

# ======================================================
# PRIORITY MAPPING FROM DAMAGE TYPE
# ======================================================

PRIORITY_FROM_DAMAGE_TYPE = {
    # +2: Extreme priority
    "protection_change_plusieur": 2,
    "prioritaire_deux": 2,

    # +1: High priority
    "prioritaire": 1,
    "prioritaire_conditionnel": 1,
    "prioritaire_critique": 1,

    # 0: Normal priority
    "offensif": 0,
    "statut": 0,
    "multi_coups": 0,
    "double_degats": 0,
    "fixe_niveau": 0,
    "fixe_degat_20": 0,
    "fixe_degat_40": 0,
    "fixe_moitie_degats": 0,
    "ko_en_un_coup": 0,
    "soin": 0,
    "variable_degats_poids": 0,
    "sommeil_requis": 0,
    "attk_adversaire": 0,
    "degat_aleatoire": 0,
    "inutile": 0,
    "critique_100": 0,
    "absorption": 0,
    "piege": 0,
    "deux_tours": 0,

    # -5: Counter moves
    "renvoi_degat_double_physique": -5,
    "renvoi_degat_double_special": -5,
    "renvoi_degat_double_deux_tours": -5,
}


def get_priority_from_damage_type(damage_type: Optional[str]) -> int:
    """
    Derive move priority from the damage_type field.

    Args:
        damage_type: Raw damage_type value from CSV

    Returns:
        Priority level as integer (-5 to +2)

    Examples:
        >>> get_priority_from_damage_type("prioritaire")
        1
        >>> get_priority_from_damage_type("offensif")
        0
        >>> get_priority_from_damage_type("unknown")
        0
    """
    if not damage_type:
        return 0
    return PRIORITY_FROM_DAMAGE_TYPE.get(damage_type.strip().lower(), 0)
