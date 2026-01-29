#!/usr/bin/env python3
"""
MLflow Integration for Machine Learning Pipeline
================================================

This module provides MLflow tracking integration for the ML pipeline,
automatically logging experiments, parameters, metrics, and models.

Features:
- Automatic experiment tracking
- Hyperparameter logging
- Metrics logging (accuracy, precision, recall, F1, AUC)
- Model artifact logging
- Dataset metadata logging
- Comparison between runs

Usage:
    from machine_learning.mlflow_integration import MLflowTracker

    tracker = MLflowTracker(experiment_name="battle_winner_v2")

    with tracker.start_run(run_name="xgboost_training"):
        tracker.log_params(hyperparams)
        tracker.log_metrics(metrics)
        tracker.log_model(model, "model")
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import mlflow
import mlflow.sklearn
import mlflow.xgboost
import pandas as pd
from mlflow.tracking import MlflowClient


class MLflowTracker:
    """MLflow experiment tracking wrapper."""

    def __init__(
        self,
        experiment_name: str = "pokemon_battle_winner",
        tracking_uri: Optional[str] = None
    ):
        """
        Initialize MLflow tracker.

        Args:
            experiment_name: Name of the MLflow experiment
            tracking_uri: MLflow tracking server URI (default: http://mlflow:5001)
        """
        # Check if MLflow tracking is explicitly disabled
        if os.getenv("DISABLE_MLFLOW_TRACKING", "false").lower() == "true":
            print("ℹ️  MLflow tracking disabled via DISABLE_MLFLOW_TRACKING environment variable")
            self.experiment_name = None
            self.experiment_id = None
            return

        # Set tracking URI (default to mlflow:5001 for Docker, localhost for local dev)
        if tracking_uri is None:
            # Check if running in Docker (MLFLOW_TRACKING_URI env var)
            tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
            if tracking_uri is None:
                # Fallback: check if we can reach mlflow service (Docker)
                import socket
                import time

                # Retry MLflow connection up to 30 seconds
                for attempt in range(10):
                    try:
                        socket.create_connection(("mlflow", 5001), timeout=3)
                        tracking_uri = "http://mlflow:5001"
                        print(f"✅ MLflow detected at mlflow:5001 (attempt {attempt + 1})")
                        break
                    except (socket.error, socket.timeout):
                        if attempt < 9:
                            print(f"⏳ Waiting for MLflow... (attempt {attempt + 1}/10)")
                            time.sleep(3)
                        else:
                            # Fallback to localhost for local dev (Docker host)
                            tracking_uri = "http://localhost:5001"
                            print("⚠️ MLflow not detected, trying localhost:5001")

        # Set or create experiment
        try:
            mlflow.set_tracking_uri(tracking_uri)

            experiment = mlflow.get_experiment_by_name(experiment_name)
            if experiment is None:
                experiment_id = mlflow.create_experiment(experiment_name)
                print(f"✅ Created new experiment: {experiment_name} (ID: {experiment_id})")
            else:
                experiment_id = experiment.experiment_id
                print(f"✅ Using existing experiment: {experiment_name} (ID: {experiment_id})")

            mlflow.set_experiment(experiment_name)
            self.experiment_name = experiment_name
            self.experiment_id = experiment_id

        except Exception as e:
            print(f"⚠️ MLflow connection error: {e}")
            print(f"⚠️ Continuing without MLflow tracking...")
            self.experiment_name = None
            self.experiment_id = None

    def start_run(self, run_name: Optional[str] = None, nested: bool = False):
        """
        Start a new MLflow run.

        Args:
            run_name: Optional name for the run
            nested: Whether this is a nested run

        Returns:
            MLflow run context manager
        """
        if self.experiment_name is None:
            # Dummy context manager if MLflow unavailable
            class DummyContext:
                def __enter__(self): return self
                def __exit__(self, *args): pass
            return DummyContext()

        if run_name is None:
            run_name = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return mlflow.start_run(run_name=run_name, nested=nested)

    def log_params(self, params: Dict[str, Any]):
        """
        Log hyperparameters.

        Args:
            params: Dictionary of parameters
        """
        if self.experiment_name is None:
            return

        try:
            # Flatten nested dicts and convert to string if needed
            flat_params = {}
            for key, value in params.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        flat_params[f"{key}_{sub_key}"] = str(sub_value)
                else:
                    flat_params[key] = value

            mlflow.log_params(flat_params)
            print(f"✅ Logged {len(flat_params)} parameters")
        except Exception as e:
            print(f"⚠️ Error logging params: {e}")

    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None):
        """
        Log metrics.

        Args:
            metrics: Dictionary of metrics
            step: Optional step number for tracking over time
        """
        if self.experiment_name is None:
            return

        try:
            mlflow.log_metrics(metrics, step=step)
            print(f"✅ Logged {len(metrics)} metrics")
        except Exception as e:
            print(f"⚠️ Error logging metrics: {e}")

    def log_model(
        self,
        model: Any,
        artifact_path: str = "model",
        model_type: str = "sklearn",
        scalers: Optional[Any] = None,
        metadata: Optional[Any] = None
    ):
        """
        Log model artifact along with optional scalers and metadata.

        Args:
            model: Trained model object
            artifact_path: Path within MLflow artifacts
            model_type: Type of model ('sklearn', 'xgboost')
            scalers: Optional scalers dict to log as artifact
            metadata: Optional metadata dict to log as artifact
        """
        if self.experiment_name is None:
            return

        try:
            if model_type == "xgboost":
                mlflow.xgboost.log_model(model, artifact_path)
            else:
                mlflow.sklearn.log_model(model, artifact_path)

            print(f"✅ Logged {model_type} model to: {artifact_path}")

            # Log scalers as artifact
            if scalers is not None:
                import pickle
                import tempfile
                with tempfile.NamedTemporaryFile(mode='wb', suffix='.pkl', delete=False) as f:
                    pickle.dump(scalers, f)
                    scalers_path = f.name
                mlflow.log_artifact(scalers_path, ".")
                print(f"✅ Logged scalers artifact")
                import os
                os.remove(scalers_path)

            # Log metadata as artifact
            if metadata is not None:
                import pickle
                import tempfile
                with tempfile.NamedTemporaryFile(mode='wb', suffix='.pkl', delete=False) as f:
                    pickle.dump(metadata, f)
                    metadata_path = f.name
                mlflow.log_artifact(metadata_path, ".")
                print(f"✅ Logged metadata artifact")
                import os
                os.remove(metadata_path)

        except Exception as e:
            print(f"⚠️ Error logging model: {e}")

    def log_artifact(self, local_path: str, artifact_path: Optional[str] = None):
        """
        Log a file or directory as an artifact.

        Args:
            local_path: Local file or directory path
            artifact_path: Optional subdirectory in artifacts
        """
        if self.experiment_name is None:
            return

        try:
            mlflow.log_artifact(local_path, artifact_path)
            print(f"✅ Logged artifact: {local_path}")
        except Exception as e:
            print(f"⚠️ Error logging artifact: {e}")

    def log_dataset_info(self, dataset_info: Dict[str, Any]):
        """
        Log dataset metadata.

        Args:
            dataset_info: Dictionary with dataset information
        """
        if self.experiment_name is None:
            return

        try:
            # Log as tags for easy filtering
            mlflow.set_tags({
                f"dataset_{key}": str(value)
                for key, value in dataset_info.items()
            })
            print(f"✅ Logged dataset metadata")
        except Exception as e:
            print(f"⚠️ Error logging dataset info: {e}")

    def set_tags(self, tags: Dict[str, str]):
        """
        Set tags for the current run.

        Args:
            tags: Dictionary of tags
        """
        if self.experiment_name is None:
            return

        try:
            mlflow.set_tags(tags)
            print(f"✅ Set {len(tags)} tags")
        except Exception as e:
            print(f"⚠️ Error setting tags: {e}")

    def register_model(
        self,
        model_name: str = "battle_winner_predictor",
        description: Optional[str] = None
    ) -> Optional[str]:
        """
        Register the current run's model in MLflow Model Registry.

        Args:
            model_name: Name for the registered model
            description: Optional description

        Returns:
            Model version string (e.g., "1", "2") or None if failed
        """
        if self.experiment_name is None:
            print("⚠️ MLflow not available, skipping model registration")
            return None

        try:
            # Get current run
            run = mlflow.active_run()
            if run is None:
                print("⚠️ No active run, cannot register model")
                return None

            run_id = run.info.run_id
            model_uri = f"runs:/{run_id}/model"

            # Register model
            result = mlflow.register_model(model_uri, model_name)
            version = result.version

            # Add description if provided
            if description:
                client = MlflowClient()
                client.update_model_version(
                    name=model_name,
                    version=version,
                    description=description
                )

            print(f"✅ Registered model '{model_name}' version {version}")
            return version

        except Exception as e:
            print(f"⚠️ Error registering model: {e}")
            return None

    def promote_to_production(
        self,
        model_name: str,
        version: str,
        archive_existing: bool = True
    ) -> bool:
        """
        Promote a model version to Production stage.

        Args:
            model_name: Name of the registered model
            version: Version to promote
            archive_existing: Whether to archive existing Production models

        Returns:
            True if successful, False otherwise
        """
        if self.experiment_name is None:
            print("⚠️ MLflow not available, skipping promotion")
            return False

        try:
            client = MlflowClient()

            # Archive existing production models if requested
            if archive_existing:
                try:
                    prod_models = client.get_latest_versions(model_name, stages=["Production"])
                    for model in prod_models:
                        client.transition_model_version_stage(
                            name=model_name,
                            version=model.version,
                            stage="Archived"
                        )
                        print(f"📦 Archived previous Production version {model.version}")
                except Exception as e:
                    print(f"⚠️ Could not archive existing models: {e}")

            # Promote new version to Production
            client.transition_model_version_stage(
                name=model_name,
                version=version,
                stage="Production"
            )

            print(f"🚀 Promoted '{model_name}' version {version} to Production")
            return True

        except Exception as e:
            print(f"⚠️ Error promoting model: {e}")
            return False

    def promote_best_model(
        self,
        model_name: str,
        metric: str = "test_accuracy",
        minimum_metric_value: float = 0.80
    ) -> bool:
        """
        Automatically promote the best model based on a metric.

        Args:
            model_name: Name of the registered model
            metric: Metric to compare (e.g., 'test_accuracy', 'test_roc_auc')
            minimum_metric_value: Minimum threshold to promote

        Returns:
            True if a model was promoted, False otherwise
        """
        if self.experiment_name is None:
            print("⚠️ MLflow not available")
            return False

        try:
            client = MlflowClient()

            # Get all versions of the model
            versions = client.search_model_versions(f"name='{model_name}'")

            if not versions:
                print(f"⚠️ No versions found for model '{model_name}'")
                return False

            # Find best version based on metric
            best_version = None
            best_metric_value = minimum_metric_value

            for version in versions:
                run = client.get_run(version.run_id)
                metric_value = run.data.metrics.get(metric)

                if metric_value and metric_value > best_metric_value:
                    best_metric_value = metric_value
                    best_version = version.version

            if best_version:
                print(f"🎯 Best model: version {best_version} with {metric}={best_metric_value:.4f}")
                return self.promote_to_production(model_name, best_version)
            else:
                print(f"⚠️ No model meets threshold ({metric} > {minimum_metric_value})")
                return False

        except Exception as e:
            print(f"⚠️ Error promoting best model: {e}")
            return False

    def compare_models(
        self,
        model_name: str,
        metrics: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Compare all versions of a registered model.

        Args:
            model_name: Name of the registered model
            metrics: List of metrics to compare (default: accuracy, f1, roc_auc)

        Returns:
            DataFrame with model versions and their metrics
        """
        if self.experiment_name is None:
            print("⚠️ MLflow not available")
            return pd.DataFrame()

        if metrics is None:
            metrics = ["test_accuracy", "test_f1", "test_roc_auc"]

        try:
            import pandas as pd
            client = MlflowClient()

            # Get all versions
            versions = client.search_model_versions(f"name='{model_name}'")

            if not versions:
                print(f"⚠️ No versions found for model '{model_name}'")
                return pd.DataFrame()

            # Build comparison table
            data = []
            for version in versions:
                run = client.get_run(version.run_id)
                row = {
                    "version": version.version,
                    "stage": version.current_stage,
                    "created_at": pd.to_datetime(version.creation_timestamp, unit='ms')
                }

                # Add metrics
                for metric in metrics:
                    row[metric] = run.data.metrics.get(metric, None)

                data.append(row)

            df = pd.DataFrame(data).sort_values("version", ascending=False)
            print(f"\n📊 Model Comparison: {model_name}")
            print(df.to_string(index=False))
            return df

        except Exception as e:
            print(f"⚠️ Error comparing models: {e}")
            return pd.DataFrame()


def get_mlflow_tracker(
    experiment_name: str = "pokemon_battle_winner",
    tracking_uri: Optional[str] = None
) -> MLflowTracker:
    """
    Get or create MLflow tracker instance.

    Args:
        experiment_name: Name of the experiment
        tracking_uri: MLflow tracking server URI

    Returns:
        MLflowTracker instance
    """
    return MLflowTracker(experiment_name, tracking_uri)


def load_model_from_registry(
    model_name: str = "battle_winner_predictor",
    stage: str = "Production",
    version: Optional[str] = None,
    tracking_uri: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Load a model bundle from MLflow Model Registry.

    Args:
        model_name: Name of the registered model
        stage: Stage to load from ('Production', 'Staging', 'Archived')
        version: Specific version to load (overrides stage)
        tracking_uri: MLflow tracking server URI

    Returns:
        Dict with keys: 'model', 'scalers', 'metadata', 'version'
        or None if not found
    """
    try:
        import pickle
        import tempfile

        from mlflow.tracking import MlflowClient

        # Set tracking URI
        if tracking_uri is None:
            tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5001")

        mlflow.set_tracking_uri(tracking_uri)
        client = MlflowClient(tracking_uri=tracking_uri)

        # Get model version details
        if version:
            model_version = client.get_model_version(model_name, version)
        else:
            # Get latest version in specified stage
            versions = client.get_latest_versions(model_name, stages=[stage])
            if not versions:
                print(f"⚠️ No model found in stage '{stage}'")
                return None
            model_version = versions[0]

        print(f"📥 Loading model from registry: {model_name} v{model_version.version} ({model_version.current_stage})")

        # Load the model itself
        model_uri = f"models:/{model_name}/{model_version.version}"

        # Try to load as sklearn model (not pyfunc wrapper)
        try:
            model = mlflow.sklearn.load_model(model_uri)
        except Exception:
            # Fallback to pyfunc
            model = mlflow.pyfunc.load_model(model_uri)
            # Extract underlying model if it's a wrapper
            if hasattr(model, '_model_impl'):
                model = model._model_impl

        # Try to download artifacts (scalers, metadata)
        scalers = None
        metadata = None

        try:
            # Get run_id from model version
            run_id = model_version.run_id

            # Download artifacts to temp directory
            with tempfile.TemporaryDirectory() as tmpdir:
                # Try to download scalers
                try:
                    scalers_path = client.download_artifacts(run_id, "scalers.pkl", tmpdir)
                    with open(scalers_path, 'rb') as f:
                        scalers = pickle.load(f)
                    print(f"✅ Scalers loaded from artifacts")
                except Exception:
                    print(f"⚠️ Scalers not found in artifacts")

                # Try to download metadata
                try:
                    metadata_path = client.download_artifacts(run_id, "metadata.pkl", tmpdir)
                    with open(metadata_path, 'rb') as f:
                        metadata = pickle.load(f)
                    print(f"✅ Metadata loaded from artifacts")
                except Exception:
                    print(f"⚠️ Metadata not found in artifacts")

        except Exception as e:
            print(f"⚠️ Could not load artifacts: {e}")

        bundle = {
            'model': model,
            'scalers': scalers,
            'metadata': metadata,
            'version': model_version.version,
            'stage': model_version.current_stage,
            'run_id': model_version.run_id
        }

        print(f"✅ Model bundle loaded successfully")
        return bundle

    except Exception as e:
        print(f"⚠️ Error loading model from registry: {e}")
        import traceback
        traceback.print_exc()
        return None
