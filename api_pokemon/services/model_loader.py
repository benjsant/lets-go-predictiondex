"""
ML Model Loader
===============

Singleton class for loading and caching the trained ML model.

This module handles:
- Loading model from MLflow Model Registry (if available)
- Fallback to local file system
- Caching model, scalers, and metadata
"""

import pickle
from pathlib import Path
from typing import Any, Dict

import joblib

from api_pokemon.config import (
    MODELS_DIR,
    USE_MLFLOW_REGISTRY,
    MLFLOW_MODEL_NAME,
    MLFLOW_MODEL_STAGE,
    DEFAULT_MODEL_VERSION,
)

# MLflow Model Registry (optional)
try:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    from machine_learning.mlflow_integration import load_model_from_registry
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    load_model_from_registry = None


class PredictionModel:
    """
    Singleton to hold the loaded ML model.

    This class ensures that the model is loaded only once and reused
    across all prediction requests.

    Attributes:
        _instance: Singleton instance
        _model: The trained ML model
        _scalers: Dictionary containing fitted scalers
        _metadata: Model metadata (features, hyperparameters, etc.)
    """

    _instance = None
    _model = None
    _scalers = None
    _metadata = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self):
        """
        Load model artifacts.

        Priority:
        1. Try MLflow Model Registry (Production stage)
        2. Fallback to local files (joblib compressed or pickle)

        Environment variables (see config.py):
        - USE_MLFLOW_REGISTRY: Enable/disable registry loading
        - MLFLOW_MODEL_NAME: Model name in registry
        - MLFLOW_MODEL_STAGE: Model stage (Production, Staging, etc.)
        - MODEL_VERSION: Default version for local files

        Raises:
            FileNotFoundError: If model files are not found locally
        """
        if self._model is not None:
            return  # Already loaded

        print("🔍 Loading ML model...")

        # Try MLflow Model Registry first
        if USE_MLFLOW_REGISTRY and MLFLOW_AVAILABLE:
            try:
                print(f"   Trying MLflow Model Registry ({MLFLOW_MODEL_NAME} @ {MLFLOW_MODEL_STAGE})...")

                # Load model bundle from registry
                model_bundle = load_model_from_registry(MLFLOW_MODEL_NAME, stage=MLFLOW_MODEL_STAGE)

                if model_bundle:
                    self._model = model_bundle.get('model')
                    self._scalers = model_bundle.get('scalers')
                    self._metadata = model_bundle.get('metadata')

                    if self._model:
                        print("✅ Model loaded from MLflow Registry")
                        version_info = model_bundle.get('version', 'unknown')
                        print(f"   Version: {version_info}")
                        return
                    print("⚠️  Model bundle incomplete, falling back to local files")
                else:
                    print("⚠️  No model in registry, falling back to local files")
            except Exception as e:
                print(f"⚠️  MLflow Registry error: {e}")
                print("   Falling back to local files...")
        elif USE_MLFLOW_REGISTRY and not MLFLOW_AVAILABLE:
            print("⚠️  MLflow not available, using local files")

        # Fallback: Load from local files
        self._load_from_local_files()

    def _load_from_local_files(self):
        """Load model artifacts from local file system."""
        print("   Loading from local files...")

        model_path = MODELS_DIR / f"battle_winner_model_{DEFAULT_MODEL_VERSION}.pkl"
        scalers_path = MODELS_DIR / f"battle_winner_scalers_{DEFAULT_MODEL_VERSION}.pkl"
        metadata_path = MODELS_DIR / f"battle_winner_metadata_{DEFAULT_MODEL_VERSION}.pkl"

        if not model_path.exists():
            raise FileNotFoundError(
                f"Model file not found: {model_path}\n"
                f"Please train a model first using: python machine_learning/train_model.py"
            )

        # Try joblib first (compressed models), fallback to pickle
        try:
            self._model = joblib.load(model_path)
        except Exception:
            with open(model_path, 'rb') as f:
                self._model = pickle.load(f)

        with open(scalers_path, 'rb') as f:
            self._scalers = pickle.load(f)

        with open(metadata_path, 'rb') as f:
            self._metadata = pickle.load(f)

        print("✅ Model loaded from local files")

    @property
    def model(self) -> Any:
        """Get the loaded model, loading it if necessary."""
        if self._model is None:
            self.load()
        return self._model

    @property
    def scalers(self) -> Dict:
        """Get the loaded scalers, loading them if necessary."""
        if self._scalers is None:
            self.load()
        return self._scalers

    @property
    def metadata(self) -> Dict:
        """Get the loaded metadata, loading it if necessary."""
        if self._metadata is None:
            self.load()
        return self._metadata


# Global model instance (singleton)
prediction_model = PredictionModel()
