#!/usr/bin/env python3
"""Populate monitoring stack with realistic test predictions."""

import argparse
import os
import random
import sys
import time
from pathlib import Path
from typing import Dict, List

import requests

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8080")
API_KEY = os.getenv("API_KEY", "BgQJ2_Ur4uYKBsw6Jf4TI_yfA6u0BFwb4a1YbOSmMVQ")
MLFLOW_URL = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5001")


def print_header(text):
    """Display a formatted header."""
    print(f"\n{'='*70}")
    print(f" {text}")
    print(f"{'='*70}\n")


def check_services():
    """Check that API and MLflow are accessible."""
    print("Checking services...")

    # API
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"API accessible: {API_URL}")
        else:
            print(f"API not accessible: {response.status_code}")
            return False
    except requests.exceptions.RequestException as exc:
        print(f"API not accessible: {exc}")
        return False

    # MLflow
    try:
        response = requests.get(f"{MLFLOW_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"MLflow accessible: {MLFLOW_URL}")
        else:
            print(f"MLflow not accessible: {response.status_code}")
            return False
    except requests.exceptions.RequestException as exc:
        print(f"MLflow not accessible: {exc}")
        return False

    return True


def get_pokemon_list() -> List[Dict]:
    """Retrieve the Pokemon list from the API."""
    headers = {"X-API-Key": API_KEY}

    try:
        response = requests.get(f"{API_URL}/pokemon", headers=headers, timeout=10)
        if response.status_code == 200:
            pokemon_list = response.json()
            print(f"{len(pokemon_list)} Pokemon retrieved")
            return pokemon_list

        print(f"Error retrieving Pokemon: {response.status_code}")
        return []
    except requests.exceptions.RequestException as exc:
        print(f"Error: {exc}")
        return []


def get_pokemon_moves(pokemon_id: int, headers: Dict) -> List[str]:
    """Retrieve offensive moves for a Pokemon from the API."""
    try:
        response = requests.get(
            f"{API_URL}/pokemon/{pokemon_id}",
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            # Filter only offensive moves (those with power)
            moves = [
                move["name"]
                for move in data.get("moves", [])
                if move.get("power") is not None and move.get("power") > 0
            ]
            return moves
        return []
    except requests.exceptions.RequestException as exc:
        print(f"Error retrieving moves for Pokemon {pokemon_id}: {exc}")
        return []


def generate_predictions(n=50):
    """Generate predictions using REAL Pokemon moves."""
    print_header("GENERATING PREDICTIONS")
    print(f"Generating {n} predictions with real moves...")

    # Retrieve Pokemon list
    pokemon_list = get_pokemon_list()
    if not pokemon_list:
        print("Unable to retrieve Pokemon list")
        return 0

    # Filter Let's Go Pokemon (up to ID ~153)
    pokemon_list = [p for p in pokemon_list if p['id'] <= 153]

    if len(pokemon_list) < 10:
        print(f"Only {len(pokemon_list)} Pokemon available")
        return 0

    print(f"{len(pokemon_list)} Let's Go Pokemon available")

    success = 0
    errors = 0
    skipped = 0

    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }

    start_time = time.time()

    for i in range(n):
        # Select 2 random Pokemon
        pokemon_a = random.choice(pokemon_list)
        pokemon_b = random.choice([p for p in pokemon_list if p['id'] != pokemon_a['id']])

        # Get moves for A
        moves_a = get_pokemon_moves(pokemon_a['id'], headers)

        if not moves_a or len(moves_a) < 2:
            skipped += 1
            continue

        # Select up to 4 random moves
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
                    print(f" {i+1}/{n} predictions... ({success} success)")
            else:
                errors += 1
                if errors <= 3:
                    error_msg = response.text[:100] if response.text else f"HTTP {response.status_code}"
                    print(f"Error {response.status_code}: {error_msg}")
                    print(f" Pokemon: {pokemon_a['id']} vs {pokemon_b['id']}, Moves: {selected_moves[:2]}...")
        except requests.exceptions.RequestException as exc:
            errors += 1
            if errors <= 3:
                print(f"Exception: {str(exc)[:100]}")

        # Small delay to avoid overloading the API
        time.sleep(0.1)

    duration = time.time() - start_time

    print(f"\nPredictions generated: {success}/{n} success")
    if skipped > 0:
        print(f" {skipped} predictions skipped (not enough moves)")
    if errors > 0:
        print(f"{errors} errors")
    print(f" Duration: {duration:.1f}s")
    if success > 0:
        print(f" Throughput: {success/duration:.1f} req/s")

    return success


def create_mlflow_experiment():
    """Create a test MLflow experiment with runs."""
    print_header("CREATING MLFLOW EXPERIMENT")

    try:
        # Import mlflow here to avoid import errors if not installed
        import mlflow # pylint: disable=import-outside-toplevel
        from mlflow.tracking import MlflowClient # pylint: disable=import-outside-toplevel

        mlflow.set_tracking_uri(MLFLOW_URL)
        MlflowClient(tracking_uri=MLFLOW_URL)

        # Create demo experiment
        experiment_name = "demo_monitoring"

        try:
            experiment_id = mlflow.create_experiment(experiment_name)
            print(f"Experiment created: {experiment_name} (ID: {experiment_id})")
        except mlflow.exceptions.MlflowException:
            # Experiment already exists
            experiment = mlflow.get_experiment_by_name(experiment_name)
            experiment_id = experiment.experiment_id
            print(f"Experiment already exists: {experiment_name} (ID: {experiment_id})")

        # Create some test runs
        print(" Creating 3 test runs...")

        for i in range(3):
            with mlflow.start_run(experiment_id=experiment_id, run_name=f"demo_run_{i+1}"):
                # Log test metrics
                accuracy = 0.90 + random.random() * 0.08 # 90-98%
                precision = 0.88 + random.random() * 0.10 # 88-98%
                recall = 0.87 + random.random() * 0.11 # 87-98%

                mlflow.log_metric("accuracy", accuracy)
                mlflow.log_metric("precision", precision)
                mlflow.log_metric("recall", recall)
                mlflow.log_metric("f1_score", 2 * (precision * recall) / (precision + recall))

                # Log params
                mlflow.log_param("model_type", "XGBoost")
                mlflow.log_param("n_estimators", random.choice([100, 200, 300]))
                mlflow.log_param("max_depth", random.choice([5, 7, 10]))

                print(f" Run {i+1}/3 created (accuracy: {accuracy:.4f})")

        print("\nMLflow experiment populated successfully")
        print(f" Open MLflow: {MLFLOW_URL}")

        return True

    except ImportError:
        print("MLflow not installed")
        return False
    except mlflow.exceptions.MlflowException as exc:
        print(f"MLflow error: {exc}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Populate monitoring with test data')
    parser.add_argument('--count', type=int, default=50, help='Number of predictions to generate (default: 50)')
    parser.add_argument('--skip-mlflow', action='store_true', help='Skip MLflow experiment creation')
    args = parser.parse_args()

    print_header("POPULATING MLflow & Grafana")

    # Check services
    if not check_services():
        print("\nServices not accessible. Check that Docker is running:")
        print(" docker compose ps")
        sys.exit(1)

    # Generate predictions
    success = generate_predictions(n=args.count)

    if success < args.count * 0.3:
        print("\nFew predictions succeeded. Pokemon data may be incomplete.")

    # Create MLflow experiments
    if not args.skip_mlflow:
        create_mlflow_experiment()

    # Check Grafana
    print_header("CHECKING GRAFANA")
    try:
        response = requests.get("http://localhost:3001/api/health", timeout=5)
        if response.status_code == 200:
            print("Grafana accessible: http://localhost:3001")
            print(" Dashboard Model Performance: http://localhost:3001/d/letsgo-model")
            print(" Dashboard API Performance: http://localhost:3001/d/letsgo-api")
        else:
            print("Grafana not accessible")
    except requests.exceptions.RequestException:
        print("Grafana not accessible")

    print_header("COMPLETED")
    print(f"Predictions generated: {success}")
    print("\nNext steps:")
    print(" 1. Open Grafana: http://localhost:3001")
    print(f" 2. Open MLflow: {MLFLOW_URL}")
    print(" 3. Check metrics in the dashboards")


if __name__ == "__main__":
    main()
