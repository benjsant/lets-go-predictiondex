# docker/ml_entrypoint.py
"""
ml_entrypoint.py

Docker entrypoint script responsible for orchestrating the Machine Learning
pipeline inside the ML builder container.

This script performs the following high-level steps:
1. Waits for a PostgreSQL database to become available.
2. Optionally skips ML training if a trained model already exists.
3. Launches the ML pipeline responsible for dataset generation, training,
   evaluation, and optional hyperparameter tuning.

The script is designed to be used as the main entrypoint of a Docker container
and relies heavily on environment variables for configuration, making it
well-suited for CI/CD pipelines, Docker Compose setups, and Kubernetes jobs.

Exit Codes
----------
0 : Successful execution (database available and ML pipeline completed).
1 : Failure during database availability check or ML pipeline execution.

Environment Variables
---------------------
Database configuration:
- POSTGRES_HOST : str
    Hostname or service name of the PostgreSQL server (default: "db").
- POSTGRES_PORT : int
    PostgreSQL port (default: 5432).
- POSTGRES_DB : str
    Database name (default: "letsgo_db").
- POSTGRES_USER : str
    Database user (default: "letsgo_user").
- POSTGRES_PASSWORD : str
    Database password (default: "letsgo_password").

ML behavior configuration:
- ML_SKIP_IF_EXISTS : bool (true/false)
    Skip training if the model file already exists (default: true).
- ML_MODE : str
    Execution mode: all, dataset, train, evaluate (default: "all").
- ML_SCENARIO_TYPE : str
    Scenario generation strategy: best_move, random_move,
    all_combinations, all (default: "all").
- ML_TUNE_HYPERPARAMS : bool (true/false)
    Enable GridSearch-based hyperparameter tuning (default: true).
- ML_GRID_TYPE : str
    Grid search type: fast or extended (default: "fast").
- ML_NUM_RANDOM_SAMPLES : int
    Number of random samples for random scenarios (default: 5).
- ML_MAX_COMBINATIONS : int
    Maximum number of move combinations to generate (default: 20).

Typical Usage
-------------
This script is executed automatically when the ML builder Docker container
starts:

    python docker/ml_entrypoint.py
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
    """
    Wait until the PostgreSQL database is ready to accept connections.

    This function continuously attempts to establish a connection to the
    PostgreSQL database until either:
    - a successful connection is made, or
    - the specified timeout is exceeded.

    It is primarily intended to prevent the ML pipeline from starting before
    the database has finished initializing, which is a common issue in
    containerized environments.

    Parameters
    ----------
    timeout : int, optional
        Maximum number of seconds to wait for the database to become available
        (default: 60).

    Returns
    -------
    bool
        True if the database becomes available within the timeout period.
        False if the timeout is exceeded before a successful connection.

    Side Effects
    ------------
    - Prints progress information to stdout for visibility in container logs.
    - Introduces delays between retries using `time.sleep`.

    Failure Scenarios
    -----------------
    - PostgreSQL container is not running
    - Invalid database credentials
    - Network or service discovery issues
    """
    print("⏳ Waiting for PostgreSQL to be ready...", flush=True)
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
            print(f"✅ PostgreSQL {DB_NAME} is ready!", flush=True)
            return True
        except psycopg2.OperationalError:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                print(f"❌ Timeout waiting for PostgreSQL after {timeout}s", flush=True)
                return False
            print(f"⏳ DB not ready yet (elapsed: {int(elapsed)}s)...", flush=True)
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
                "ℹ️  Model already exists, skipping training "
                "(set ML_SKIP_IF_EXISTS=false to force retrain)",
                flush=True
            )
            return True
        else:
            print(
                "ℹ️  Model exists but ML_SKIP_IF_EXISTS=false, retraining...",
                flush=True
            )

    print("🚀 Starting ML pipeline v2 (multi-scenarios)...", flush=True)

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

    print("📋 Configuration:", flush=True)
    print(f"   Mode: {mode}", flush=True)
    print(f"   Scenario: {scenario_type}", flush=True)
    print(f"   Hyperparameter tuning: {tune_hyperparams}", flush=True)
    print(f"   Grid type: {grid_type}", flush=True)
    print(f"   Random samples: {num_random_samples}", flush=True)
    print(f"   Max combinations: {max_combinations}", flush=True)

    result = subprocess.run(cmd, check=False)

    if result.returncode == 0:
        print("✅ ML pipeline v2 completed successfully!", flush=True)
        return True
    else:
        print(
            f"❌ ML pipeline failed with exit code {result.returncode}",
            flush=True
        )
        return False


def main():
    """
    Main container entrypoint.

    This function coordinates the full lifecycle of the ML builder container:
    1. Logs container startup.
    2. Waits for the PostgreSQL database to become available.
    3. Executes the ML pipeline.
    4. Exits with an appropriate status code for Docker or CI/CD systems.
    """
    print("🐳 ML Builder Container Starting...", flush=True)

    # Wait for database availability
    if not wait_for_db(timeout=60):
        print("❌ Database not available. Exiting.", flush=True)
        sys.exit(1)

    # Run ML pipeline
    if not run_ml_builder():
        print("❌ ML builder failed. Exiting.", flush=True)
        sys.exit(1)

    print("✅ ML builder container finished successfully.", flush=True)
    sys.exit(0)


if __name__ == "__main__":
    main()
