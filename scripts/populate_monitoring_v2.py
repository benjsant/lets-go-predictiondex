#!/usr/bin/env python3
"""
Populate Monitoring Stack with Real Test Data
==============================================

This script generates realistic test predictions for MLflow and Grafana monitoring.

The script queries the API to fetch REAL moves for each Pokémon before making
predictions, ensuring valid and realistic data for monitoring validation.

Features:
    - Fetches actual Pokémon moves from the API
    - Generates N battle predictions with real move combinations
    - Populates Prometheus metrics via API calls
    - Creates MLflow experiment runs with test metrics
    - Validates monitoring stack functionality

Usage:
    # Generate 50 predictions (default)
    python3 scripts/populate_monitoring_v2.py

    # Generate custom number of predictions
    python3 scripts/populate_monitoring_v2.py --count 100

    # Skip MLflow experiment creation
    python3 scripts/populate_monitoring_v2.py --count 50 --skip-mlflow

Args:
    --count: Number of predictions to generate (default: 50)
    --skip-mlflow: Skip MLflow experiment creation
"""

import argparse
import os
import random
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

import requests

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8080")
API_KEY = os.getenv("API_KEY", "BgQJ2_Ur4uYKBsw6Jf4TI_yfA6u0BFwb4a1YbOSmMVQ")
MLFLOW_URL = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5001")

def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def check_services():
    """Vérifie que l'API et MLflow sont accessibles."""
    print("🔍 Vérification des services...")

    # API
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ API accessible : {API_URL}")
        else:
            print(f"❌ API non accessible : {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API non accessible : {e}")
        return False

    # MLflow
    try:
        response = requests.get(f"{MLFLOW_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ MLflow accessible : {MLFLOW_URL}")
        else:
            print(f"❌ MLflow non accessible : {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ MLflow non accessible : {e}")
        return False

    return True

def get_pokemon_list() -> List[Dict]:
    """Récupère la liste des Pokémon depuis l'API."""
    headers = {"X-API-Key": API_KEY}

    try:
        response = requests.get(f"{API_URL}/pokemon", headers=headers, timeout=10)
        if response.status_code == 200:
            pokemon_list = response.json()
            print(f"✅ {len(pokemon_list)} Pokémon récupérés")
            return pokemon_list
        else:
            print(f"❌ Erreur récupération Pokémon: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return []

def get_pokemon_moves(pokemon_id: int, headers: Dict) -> List[str]:
    """Récupère les moves offensifs d'un Pokémon depuis l'API."""
    try:
        response = requests.get(
            f"{API_URL}/pokemon/{pokemon_id}",
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            # Filtrer uniquement les moves offensifs (ceux avec power)
            moves = [
                move["name"]  # La clé est "name", pas "move_name"
                for move in data.get("moves", [])
                if move.get("power") is not None and move.get("power") > 0
            ]
            return moves
        return []
    except Exception as e:
        print(f"⚠️  Erreur récupération moves Pokémon {pokemon_id}: {e}")
        return []

def generate_predictions(n=50):
    """Génère des prédictions en utilisant les VRAIS moves des Pokémon."""
    print_header("GÉNÉRATION DE PRÉDICTIONS")
    print(f"📊 Génération de {n} prédictions avec des moves réels...")

    # Récupérer la liste des Pokémon
    pokemon_list = get_pokemon_list()
    if not pokemon_list:
        print("❌ Impossible de récupérer la liste des Pokémon")
        return 0

    # Filtrer les Pokémon Let's Go (jusqu'au ID ~153)
    pokemon_list = [p for p in pokemon_list if p['id'] <= 153]

    if len(pokemon_list) < 10:
        print(f"⚠️  Seulement {len(pokemon_list)} Pokémon disponibles")
        return 0

    print(f"✅ {len(pokemon_list)} Pokémon Let's Go disponibles")

    success = 0
    errors = 0
    skipped = 0

    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }

    start_time = time.time()

    for i in range(n):
        # Sélectionner 2 Pokémon aléatoires
        pokemon_a = random.choice(pokemon_list)
        pokemon_b = random.choice([p for p in pokemon_list if p['id'] != pokemon_a['id']])

        # Récupérer les moves de A
        moves_a = get_pokemon_moves(pokemon_a['id'], headers)

        if not moves_a or len(moves_a) < 2:
            skipped += 1
            continue

        # Sélectionner 4 moves aléatoires maximum
        selected_moves = random.sample(moves_a, min(4, len(moves_a)))

        payload = {
            "pokemon_a_id": pokemon_a['id'],
            "pokemon_b_id": pokemon_b['id'],
            "available_moves": selected_moves
        }

        try:
            response = requests.post(
                f"{API_URL}/predict/best-move",
                headers=headers,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                success += 1
                if (i + 1) % 10 == 0:
                    print(f"   {i+1}/{n} prédictions... ({success} succès)")
            else:
                errors += 1
                if errors <= 3:
                    error_msg = response.text[:100] if response.text else f"HTTP {response.status_code}"
                    print(f"⚠️  Erreur {response.status_code}: {error_msg}")
                    print(f"   Pokémon: {pokemon_a['id']} vs {pokemon_b['id']}, Moves: {selected_moves[:2]}...")
        except Exception as e:
            errors += 1
            if errors <= 3:
                print(f"⚠️  Exception : {str(e)[:100]}")

        # Petit délai pour ne pas surcharger l'API
        time.sleep(0.1)

    duration = time.time() - start_time

    print(f"\n✅ Prédictions générées : {success}/{n} succès")
    if skipped > 0:
        print(f"⏭️  {skipped} prédictions sautées (pas assez de moves)")
    if errors > 0:
        print(f"⚠️  {errors} erreurs")
    print(f"   Durée : {duration:.1f}s")
    if success > 0:
        print(f"   Throughput : {success/duration:.1f} req/s")

    return success

def create_mlflow_experiment():
    """Crée une expérience MLflow de test avec des runs."""
    print_header("CRÉATION D'EXPÉRIENCE MLFLOW")

    try:
        import mlflow
        from mlflow.tracking import MlflowClient

        mlflow.set_tracking_uri(MLFLOW_URL)
        client = MlflowClient(tracking_uri=MLFLOW_URL)

        # Créer une expérience de démo
        experiment_name = "demo_monitoring"

        try:
            experiment_id = mlflow.create_experiment(experiment_name)
            print(f"✅ Expérience créée : {experiment_name} (ID: {experiment_id})")
        except Exception:
            # L'expérience existe déjà
            experiment = mlflow.get_experiment_by_name(experiment_name)
            experiment_id = experiment.experiment_id
            print(f"ℹ️  Expérience existe déjà : {experiment_name} (ID: {experiment_id})")

        # Créer quelques runs de test
        print(f"📝 Création de 3 runs de test...")

        for i in range(3):
            with mlflow.start_run(experiment_id=experiment_id, run_name=f"demo_run_{i+1}"):
                # Log des métriques de test
                accuracy = 0.90 + random.random() * 0.08  # 90-98%
                precision = 0.88 + random.random() * 0.10  # 88-98%
                recall = 0.87 + random.random() * 0.11     # 87-98%

                mlflow.log_metric("accuracy", accuracy)
                mlflow.log_metric("precision", precision)
                mlflow.log_metric("recall", recall)
                mlflow.log_metric("f1_score", 2 * (precision * recall) / (precision + recall))

                # Log des params
                mlflow.log_param("model_type", "XGBoost")
                mlflow.log_param("n_estimators", random.choice([100, 200, 300]))
                mlflow.log_param("max_depth", random.choice([5, 7, 10]))

                print(f"   ✅ Run {i+1}/3 créé (accuracy: {accuracy:.4f})")

        print(f"\n✅ Expérience MLflow peuplée avec succès")
        print(f"   Ouvrez MLflow : {MLFLOW_URL}")

        return True

    except Exception as e:
        print(f"❌ Erreur MLflow: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Peupler le monitoring avec des données de test')
    parser.add_argument('--count', type=int, default=50, help='Nombre de prédictions à générer (default: 50)')
    parser.add_argument('--skip-mlflow', action='store_true', help='Skip MLflow experiment creation')
    args = parser.parse_args()

    print_header("🚀 POPULATION MLflow & Grafana")

    # Vérifier services
    if not check_services():
        print("\n❌ Services non accessibles. Vérifiez que Docker est lancé:")
        print("   docker compose ps")
        sys.exit(1)

    # Générer prédictions
    success = generate_predictions(n=args.count)

    if success < args.count * 0.3:
        print("\n⚠️  Peu de prédictions réussies. Les données Pokémon sont peut-être incomplètes.")

    # Créer expériences MLflow
    if not args.skip_mlflow:
        create_mlflow_experiment()

    # Vérifier Grafana
    print_header("VÉRIFICATION GRAFANA")
    try:
        response = requests.get(f"http://localhost:3001/api/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Grafana accessible : http://localhost:3001")
            print(f"   Dashboard Model Performance: http://localhost:3001/d/letsgo-model")
            print(f"   Dashboard API Performance: http://localhost:3001/d/letsgo-api")
        else:
            print(f"⚠️  Grafana non accessible")
    except Exception:
        print(f"⚠️  Grafana non accessible")

    print_header("✅ TERMINÉ")
    print(f"Prédictions générées : {success}")
    print(f"\nProchaines étapes :")
    print(f"  1. Ouvrez Grafana : http://localhost:3001")
    print(f"  2. Ouvrez MLflow : {MLFLOW_URL}")
    print(f"  3. Vérifiez les métriques dans les dashboards")

if __name__ == "__main__":
    main()
