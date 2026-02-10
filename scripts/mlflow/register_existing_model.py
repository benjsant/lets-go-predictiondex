#!/usr/bin/env python3
"""
Script to register the existing model in MLflow Model Registry.

Registers model v2 (96.24% accuracy) that already exists on disk.
"""
import json
import os
import pickle
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to PYTHONPATH before importing local modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import mlflow  # pylint: disable=wrong-import-position
from mlflow.tracking import MlflowClient  # pylint: disable=wrong-import-position

from machine_learning.mlflow_integration import (  # pylint: disable=wrong-import-position
    get_mlflow_tracker
)

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_section(title):
    """Display a formatted section header."""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{title:^80}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")


def print_success(msg):
    """Display a success message."""
    print(f"{GREEN}✅ {msg}{RESET}")


def print_error(msg):
    """Display an error message."""
    print(f"{RED}❌ {msg}{RESET}")


def print_info(msg):
    """Display an info message."""
    print(f"   {msg}")


def check_mlflow_connection():
    """Check that MLflow is accessible."""
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5001")
    mlflow.set_tracking_uri(tracking_uri)

    try:
        # Test connection
        mlflow.search_experiments()
        print_success(f"MLflow connected: {tracking_uri}")
        return True
    except mlflow.exceptions.MlflowException as exc:
        print_error(f"MLflow not accessible: {exc}")
        print_info("Make sure MLflow is started:")
        print_info("  docker compose ps mlflow")
        print_info("  curl http://localhost:5001/health")
        return False


def register_model_v2():
    """Register the existing v2 model in MLflow."""
    print_section("REGISTERING MODEL V2 IN MLFLOW")

    # Paths to the model
    models_dir = Path(__file__).parent.parent.parent / "models"
    model_path = models_dir / "battle_winner_model_v2.pkl"
    scalers_path = models_dir / "battle_winner_scalers_v2.pkl"
    metadata_path = models_dir / "battle_winner_metadata_v2.json"

    # Check that files exist
    if not model_path.exists():
        print_error(f"Model not found: {model_path}")
        return False

    print_info(f"Loading model: {model_path}")

    # Load the model
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        print_success("Model loaded")
    except (OSError, pickle.UnpicklingError) as exc:
        print_error(f"Error loading model: {exc}")
        return False

    # Load scalers
    scalers = None
    try:
        with open(scalers_path, 'rb') as f:
            scalers = pickle.load(f)
        print_success("Scalers loaded")
    except (OSError, pickle.UnpicklingError) as exc:
        print_error(f"Error loading scalers: {exc}")

    # Load metadata
    metadata = {}
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        print_success("Metadata loaded")

        # Display metrics
        metrics = metadata.get('metrics', {})
        print_info(f"  - Accuracy: {metrics.get('test_accuracy', 0)*100:.2f}%")
        print_info(f"  - ROC-AUC: {metrics.get('test_roc_auc', 0)*100:.2f}%")
        print_info(f"  - F1-Score: {metrics.get('test_f1', 0)*100:.2f}%")

    except (OSError, json.JSONDecodeError) as exc:
        print_error(f"Error loading metadata: {exc}")

    # Create MLflow tracker
    print_info("\nCreating MLflow tracker...")

    try:
        # Force MLflow activation
        os.environ["DISABLE_MLFLOW_TRACKING"] = "false"

        tracker = get_mlflow_tracker(experiment_name="pokemon_battle_winner")

        if tracker.experiment_name is None:
            print_error("MLflow tracking is disabled")
            print_info("Set DISABLE_MLFLOW_TRACKING=false")
            return False

        print_success(f"Tracker created - Experiment: {tracker.experiment_name}")

    except mlflow.exceptions.MlflowException as exc:
        print_error(f"Error creating tracker: {exc}")
        return False

    # Start a run
    run_name = f"register_existing_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print_info(f"\nStarting run: {run_name}")

    try:
        tracker.start_run(run_name=run_name)
        print_success("Run started")
    except mlflow.exceptions.MlflowException as exc:
        print_error(f"Error starting run: {exc}")
        return False

    # Log parameters
    print_info("\nLogging hyperparameters...")
    try:
        params = metadata.get('hyperparameters', {})
        params['model_version'] = metadata.get('version', 'v2')
        params['dataset_version'] = metadata.get('dataset_version', 'v2')
        params['n_features'] = metadata.get('n_features', 133)

        tracker.log_params(params)
        print_success(f"{len(params)} parameters logged")
    except mlflow.exceptions.MlflowException as exc:
        print_error(f"Error logging parameters: {exc}")

    # Log metrics
    print_info("\nLogging metrics...")
    try:
        metrics_to_log = metadata.get('metrics', {})
        tracker.log_metrics(metrics_to_log)
        print_success(f"{len(metrics_to_log)} metrics logged")
    except mlflow.exceptions.MlflowException as exc:
        print_error(f"Error logging metrics: {exc}")

    # Log the model
    print_info("\nLogging model...")
    try:
        # Prepare metadata for MLflow
        mlflow_metadata = {
            'model_type': metadata.get('model_type', 'XGBClassifier'),
            'version': metadata.get('version', 'v2'),
            'training_date': metadata.get('training_date'),
            'n_features': metadata.get('n_features'),
            'feature_columns': metadata.get('feature_columns', [])
        }

        tracker.log_model(
            model=model,
            artifact_path="model",
            model_type='xgboost',
            scalers=scalers,
            metadata=mlflow_metadata
        )
        print_success("Model logged with scalers and metadata")
    except mlflow.exceptions.MlflowException as exc:
        print_error(f"Error logging model: {exc}")
        tracker.end_run()
        return False

    # Register in Model Registry
    print_info("\nRegistering in Model Registry...")
    metrics = metadata.get('metrics', {})
    try:
        model_name = "battle_winner_predictor"
        description = (
            f"Pokémon Battle Winner Predictor v2\n"
            f"Accuracy: {metrics.get('test_accuracy', 0)*100:.2f}%\n"
            f"ROC-AUC: {metrics.get('test_roc_auc', 0)*100:.2f}%\n"
            f"Training Date: {metadata.get('training_date', 'N/A')}\n"
            f"Features: {metadata.get('n_features', 133)}\n"
            f"Training Samples: {metrics.get('train_samples', 0):,}\n"
            f"Test Samples: {metrics.get('test_samples', 0):,}"
        )

        version_number = tracker.register_model(
            model_name=model_name,
            description=description
        )

        if version_number:
            print_success(f"Model registered: {model_name} version {version_number}")

            # Promote to Production if accuracy >= 95%
            test_accuracy = metrics.get('test_accuracy', 0)
            if test_accuracy >= 0.95:
                print_info("\nPromoting to Production...")
                success = tracker.promote_to_production(model_name, version_number)
                if success:
                    print_success(
                        f"Model promoted to Production (Accuracy: {test_accuracy*100:.2f}%)"
                    )
                else:
                    print_error("Failed to promote to Production")
            else:
                print_info(
                    f"\nAccuracy {test_accuracy*100:.2f}% < 95%, no automatic promotion"
                )
                print_info("To promote manually:")
                print_info('  python -c "')
                print_info("  from machine_learning.mlflow_integration import MLflowTracker")
                print_info("  tracker = MLflowTracker('pokemon_battle_winner')")
                print_info(f"  tracker.promote_to_production('{model_name}', {version_number})")
                print_info('  "')
        else:
            print_error("Failed to register model")

    except mlflow.exceptions.MlflowException as exc:
        print_error(f"Error during registration: {exc}")
        mlflow.end_run()
        return False

    # End the run
    mlflow.end_run()
    print_success("\nRun completed")

    return True


def verify_registration():
    """Verify that the model is properly registered."""
    print_section("VERIFYING REGISTRATION")

    try:
        # List experiments
        experiments = mlflow.search_experiments()
        print_info(f"Experiments found: {len(experiments)}")
        for exp in experiments:
            print_info(f"  - {exp.name} (ID: {exp.experiment_id})")

        # List registered models
        client = MlflowClient()

        try:
            registered_models = client.search_registered_models()
            print_info(f"\nRegistered models: {len(registered_models)}")

            for rm in registered_models:
                print_success(f"\n📦 Model: {rm.name}")
                if rm.description:
                    print_info(f"   Description: {rm.description[:100]}...")

                # List versions
                versions = client.search_model_versions(f"name='{rm.name}'")
                for mv in versions:
                    stage = mv.current_stage
                    emoji = "🏆" if stage == "Production" else "📝"
                    print_info(f"   {emoji} Version {mv.version}: Stage={stage}")

        except mlflow.exceptions.MlflowException as exc:
            print_error(f"Unable to list models: {exc}")

        return True

    except mlflow.exceptions.MlflowException as exc:
        print_error(f"Error during verification: {exc}")
        return False


def main():
    """Main function."""
    print_section("REGISTERING MODEL V2 IN MLFLOW")

    print_info("This script will:")
    print_info("  1. Load the existing v2 model (96.24% accuracy)")
    print_info("  2. Create an MLflow experiment")
    print_info("  3. Log model, metrics, and hyperparameters")
    print_info("  4. Register in MLflow Model Registry")
    print_info("  5. Promote to Production if accuracy >= 95%")

    # Check MLflow connection
    if not check_mlflow_connection():
        return 1

    # Register the model
    if not register_model_v2():
        print_error("\n❌ REGISTRATION FAILED")
        return 1

    # Verify registration
    if not verify_registration():
        print_error("\n❌ VERIFICATION FAILED")
        return 1

    print_section("SUCCESS")
    print_success("Model v2 registered in MLflow!")
    print_info("\nCheck in MLflow UI:")
    print_info("  http://localhost:5001")
    print_info("\nTo use the model from MLflow in the API:")
    print_info("  Modify docker-compose.yml line 128:")
    print_info('    USE_MLFLOW_REGISTRY: "true"')
    print_info("  Then restart: docker compose restart api")

    return 0


if __name__ == "__main__":
    sys.exit(main())
