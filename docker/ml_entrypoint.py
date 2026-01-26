#docker/ml_entrypoint.py
"""
ML Builder Entrypoint - Wait for DB and build ML dataset
"""
import subprocess
import sys
import time
import os
import psycopg2

# Database connection from environment
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
DB_USER = os.getenv("POSTGRES_USER", "letsgo_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "letsgo_password")
DB_NAME = os.getenv("POSTGRES_DB", "letsgo_db")


def wait_for_db(timeout=60):
    """Wait for PostgreSQL to be ready."""
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
        except psycopg2.OperationalError as e:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                print(f"❌ Timeout waiting for PostgreSQL after {timeout}s", flush=True)
                return False
            print(f"⏳ DB not ready yet (elapsed: {int(elapsed)}s)...", flush=True)
            time.sleep(2)


def run_ml_builder():
    """Run the complete ML pipeline (v2 multi-scenarios with GridSearch)."""
    
    # Check if model already exists (skip re-training)
    model_path = "/app/models/battle_winner_model_v2.pkl"
    if os.path.exists(model_path):
        skip_training = os.getenv("ML_SKIP_IF_EXISTS", "true").lower() == "true"
        if skip_training:
            print("ℹ️  Model already exists, skipping training (set ML_SKIP_IF_EXISTS=false to force retrain)", flush=True)
            return True
        else:
            print("ℹ️  Model exists but ML_SKIP_IF_EXISTS=false, retraining...", flush=True)
    
    print("🚀 Starting ML pipeline v2 (multi-scenarios)...", flush=True)
    
    # Get configuration from environment variables
    mode = os.getenv("ML_MODE", "all")  # all, dataset, train, evaluate
    scenario_type = os.getenv("ML_SCENARIO_TYPE", "all")  # best_move, random_move, all_combinations, all
    tune_hyperparams = os.getenv("ML_TUNE_HYPERPARAMS", "true").lower() == "true"
    grid_type = os.getenv("ML_GRID_TYPE", "fast")  # fast or extended
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
    
    print(f"📋 Configuration:", flush=True)
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
        print(f"❌ ML pipeline failed with exit code {result.returncode}", flush=True)
        return False


def main():
    """Main entrypoint."""
    print("🐳 ML Builder Container Starting...", flush=True)

    # Wait for database
    if not wait_for_db(timeout=60):
        print("❌ Database not available. Exiting.", flush=True)
        sys.exit(1)

    # Run ML builder
    if not run_ml_builder():
        print("❌ ML builder failed. Exiting.", flush=True)
        sys.exit(1)

    print("✅ ML builder container finished successfully.", flush=True)
    sys.exit(0)


if __name__ == "__main__":
    main()
