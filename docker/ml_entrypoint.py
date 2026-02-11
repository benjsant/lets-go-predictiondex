# docker/ml_entrypoint.py
"""Docker entrypoint for the ML builder container.

Waits for PostgreSQL, then runs the ML training pipeline.
Configuration is driven by environment variables (ML_MODE, ML_SKIP_IF_EXISTS, etc.).
"""

import subprocess
import sys
import time
import os
import psycopg2

# Database connection parameters retrieved from environment variables.
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
DB_USER = os.getenv("POSTGRES_USER", "letsgo_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "letsgo_password")
DB_NAME = os.getenv("POSTGRES_DB", "letsgo_db")


def wait_for_db(timeout=60):
    """Wait for PostgreSQL to be ready, retrying until timeout."""
    print("[WAIT] Waiting for PostgreSQL to be ready...", flush=True)
    start_time = time.time()

    while True:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                dbname=DB_NAME,
                connect_timeout=3
            )
            conn.close()
            print(f"[OK] PostgreSQL {DB_NAME} is ready!", flush=True)
            return True
        except psycopg2.OperationalError:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                print(f"[ERROR] Timeout waiting for PostgreSQL after {timeout}s", flush=True)
                return False
            print(f"[WAIT] DB not ready yet (elapsed: {int(elapsed)}s)...", flush=True)
            time.sleep(2)


def run_ml_builder():
    """
    Execute the complete Machine Learning pipeline.

    This function orchestrates the execution of the ML workflow, including:
    - optional dataset generation,
    - model training,
    - evaluation,
    - and optional hyperparameter tuning using GridSearch.

    The behavior of the pipeline is fully driven by environment variables,
    allowing flexible execution modes without modifying code.

    If a trained model already exists on disk, the function may skip training
    depending on the value of the `ML_SKIP_IF_EXISTS` environment variable.

    Returns
    -------
    bool
        True if the ML pipeline completes successfully.
        False if the pipeline fails or returns a non-zero exit code.

    Side Effects
    ------------
    - Executes an external Python process via `subprocess.run`.
    - Reads configuration from environment variables.
    - Writes logs to stdout for container-level observability.
    """
    # Check if model already exists (skip re-training)
    model_path = "/app/models/battle_winner_model_v2.pkl"
    if os.path.exists(model_path):
        skip_training = os.getenv("ML_SKIP_IF_EXISTS", "true").lower() == "true"
        if skip_training:
            print(
                "[INFO] Model already exists, skipping training "
                "(set ML_SKIP_IF_EXISTS=false to force retrain)",
                flush=True
            )
            return True
        else:
            print(
                "[INFO] Model exists but ML_SKIP_IF_EXISTS=false, retraining...",
                flush=True
            )

    print("[START] Starting ML pipeline v2 (multi-scenarios)...", flush=True)

    # Retrieve ML configuration from environment variables
    mode = os.getenv("ML_MODE", "all")
    scenario_type = os.getenv("ML_SCENARIO_TYPE", "all")
    tune_hyperparams = os.getenv("ML_TUNE_HYPERPARAMS", "true").lower() == "true"
    grid_type = os.getenv("ML_GRID_TYPE", "fast")
    num_random_samples = int(os.getenv("ML_NUM_RANDOM_SAMPLES", "5"))
    max_combinations = int(os.getenv("ML_MAX_COMBINATIONS", "20"))

    cmd = [
        "python", "machine_learning/run_machine_learning.py",
        "--mode", mode,
        "--dataset-version", "v2",
        "--scenario-type", scenario_type,
        "--version", "v2",
        "--num-random-samples", str(num_random_samples),
        "--max-combinations", str(max_combinations),
        "--grid-type", grid_type
    ]

    if tune_hyperparams:
        cmd.append("--tune-hyperparams")

    print("[CONFIG] Configuration:", flush=True)
    print(f"   Mode: {mode}", flush=True)
    print(f"   Scenario: {scenario_type}", flush=True)
    print(f"   Hyperparameter tuning: {tune_hyperparams}", flush=True)
    print(f"   Grid type: {grid_type}", flush=True)
    print(f"   Random samples: {num_random_samples}", flush=True)
    print(f"   Max combinations: {max_combinations}", flush=True)

    result = subprocess.run(cmd, check=False)

    if result.returncode == 0:
        print("[OK] ML pipeline v2 completed successfully!", flush=True)
        return True
    else:
        print(
            f"[ERROR] ML pipeline failed with exit code {result.returncode}",
            flush=True
        )
        return False


def main():
    """Main container entrypoint for the ML builder."""
    print("[DOCKER] ML Builder Container Starting...", flush=True)

    # Wait for database availability
    if not wait_for_db(timeout=60):
        print("[ERROR] Database not available. Exiting.", flush=True)
        sys.exit(1)

    # Run ML pipeline
    if not run_ml_builder():
        print("[ERROR] ML builder failed. Exiting.", flush=True)
        sys.exit(1)

    print("[OK] ML builder container finished successfully.", flush=True)
    sys.exit(0)


if __name__ == "__main__":
    main()
