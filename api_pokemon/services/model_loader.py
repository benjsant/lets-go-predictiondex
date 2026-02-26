import pickle
from pathlib import Path
from typing import Any, Dict, Optional

import joblib

from api_pokemon.config import (
    MODELS_DIR,
    USE_MLFLOW_REGISTRY,
    MLFLOW_MODEL_NAME,
    MLFLOW_MODEL_STAGE,
    DEFAULT_MODEL_VERSION,
)

try:
    from machine_learning.mlflow_integration import load_model_from_registry
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    load_model_from_registry = None


class PredictionModel:
    """Singleton holding the loaded ML model (lazy-loaded on first access)."""

    _instance = None
    _model = None
    _scalers = None
    _metadata = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self):
        if self._model is not None:
            return

        print("[Model] Loading ML model...")

        if USE_MLFLOW_REGISTRY and MLFLOW_AVAILABLE:
            try:
                print(f"[Model] Trying MLflow Registry ({MLFLOW_MODEL_NAME} @ {MLFLOW_MODEL_STAGE})...")

                model_bundle = load_model_from_registry(MLFLOW_MODEL_NAME, stage=MLFLOW_MODEL_STAGE)

                if model_bundle:
                    self._model = model_bundle.get('model')
                    self._scalers = model_bundle.get('scalers')
                    self._metadata = model_bundle.get('metadata')

                    if self._model:
                        version_info = model_bundle.get('version', 'unknown')
                        print(f"[Model] Loaded from MLflow Registry (version: {version_info})")
                        return
                    print("[Model] Warning: Bundle incomplete, falling back to local files")
                else:
                    print("[Model] Warning: No model in registry, falling back to local files")
            except Exception as e:
                print(f"[Model] Warning: MLflow Registry error: {e}")
                print("[Model] Falling back to local files...")
        elif USE_MLFLOW_REGISTRY and not MLFLOW_AVAILABLE:
            print("[Model] Warning: MLflow not available, using local files")

        self._load_from_local_files()

    def _load_from_local_files(self):
        print("[Model] Loading from local files...")

        model_path = MODELS_DIR / f"battle_winner_model_{DEFAULT_MODEL_VERSION}.pkl"
        scalers_path = MODELS_DIR / f"battle_winner_scalers_{DEFAULT_MODEL_VERSION}.pkl"
        metadata_path = MODELS_DIR / f"battle_winner_metadata_{DEFAULT_MODEL_VERSION}.pkl"

        if not model_path.exists():
            raise FileNotFoundError(
                f"Model file not found: {model_path}\n"
                f"Please train a model first using: python machine_learning/train_model.py"
            )

        try:
            self._model = joblib.load(model_path)
        except Exception:
            with open(model_path, 'rb') as f:
                self._model = pickle.load(f)

        with open(scalers_path, 'rb') as f:
            self._scalers = pickle.load(f)

        with open(metadata_path, 'rb') as f:
            self._metadata = pickle.load(f)

        print("[Model] Loaded from local files")

    @property
    def model(self) -> Any:
        if self._model is None:
            self.load()
        return self._model

    @property
    def scalers(self) -> Optional[Dict]:
        if self._scalers is None:
            self.load()
        return self._scalers

    @property
    def metadata(self) -> Optional[Dict]:
        if self._metadata is None:
            self.load()
        return self._metadata


prediction_model = PredictionModel()
