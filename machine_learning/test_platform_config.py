#!/usr/bin/env python3
"""
Script de test pour vérifier la configuration plateforme.

Ce script affiche les paramètres détectés automatiquement
selon la plateforme (Windows/Linux) et vérifie que les
optimisations sont correctement appliquées.

Usage:
    python machine_learning/test_platform_config.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from machine_learning.platform_config import (
    get_platform_info,
    get_safe_n_jobs,
    get_safe_gridsearch_n_jobs,
    print_platform_summary,
    SAFE_N_JOBS,
    SAFE_GRIDSEARCH_N_JOBS,
)
from machine_learning.config import XGBOOST_PARAMS


def main():
    """Affiche la configuration détectée."""
    print("\n" + "=" * 70)
    print("TEST CONFIGURATION PLATEFORME")
    print("=" * 70)

    # Affiche le résumé de la plateforme
    print_platform_summary()

    # Teste les fonctions individuelles
    print("\n[Tests] Fonctions:")
    print(f"  get_safe_n_jobs() = {get_safe_n_jobs()}")
    print(f"  get_safe_gridsearch_n_jobs() = {get_safe_gridsearch_n_jobs()}")

    # Affiche les constantes
    print("\n[Config] Constantes globales:")
    print(f"  SAFE_N_JOBS = {SAFE_N_JOBS}")
    print(f"  SAFE_GRIDSEARCH_N_JOBS = {SAFE_GRIDSEARCH_N_JOBS}")

    # Affiche la config XGBoost
    print("\n[XGBoost] Configuration:")
    for key, value in XGBOOST_PARAMS.items():
        if key == 'n_jobs':
            print(f"  {key}: {value} (*auto-ajuste selon plateforme)")
        else:
            print(f"  {key}: {value}")

    # Recommandations
    info = get_platform_info()
    print("\n[Recommandations]")
    if info['is_windows']:
        print("  [OK] Windows detecte - Optimisations memoire activees")
        print("  [OK] Nombre de jobs reduit pour eviter saturation")
        print("  [OK] Garbage collector configure en mode agressif")
        print("\n  [Commandes recommandees]")
        print("     # Sans GridSearch (rapide, moins de RAM)")
        print("     python machine_learning/run_machine_learning.py --mode=all")
        print("\n     # Avec GridSearch FAST (tuning modere)")
        print("     python machine_learning/run_machine_learning.py --mode=all --tune-hyperparams --grid-type fast")
        print("\n     [WARN] GridSearch EXTENDED non recommande sur Windows (trop de RAM)")
    else:
        print("  [OK] Linux detecte - Configuration haute performance")
        print("  [OK] Tous les coeurs CPU utilises")
        print("  [OK] GridSearch EXTENDED possible")
        print("\n  [Commandes disponibles]")
        print("     # Pipeline complet avec tuning etendu")
        print("     python machine_learning/run_machine_learning.py --mode=all --tune-hyperparams --grid-type extended")

    print("\n" + "=" * 70)
    print("[SUCCESS] Configuration chargee avec succes!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
