import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd


class DriftDetector:
    """Collects production predictions for future drift analysis and retraining."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return

        self._initialized = True
        self.logger = logging.getLogger(__name__)

        self.monitoring_dir = Path(__file__).parent
        self.drift_data_dir = self.monitoring_dir / "drift_data"
        self.drift_data_dir.mkdir(parents=True, exist_ok=True)

        self.production_buffer: List[Dict] = []
        self.max_buffer_size = 100

        self.reference_data: Optional[pd.DataFrame] = None
        self._load_reference_data()

    def _load_reference_data(self):
        try:
            ref_file = Path("data/ml/battle_winner_v2/features/X_train.parquet")
            if not ref_file.exists():
                ref_file = Path("/app/data/ml/battle_winner_v2/features/X_train.parquet")

            if not ref_file.exists():
                self.logger.warning(
                    "Reference data file not found: %s. "
                    "This is optional for production data collection.",
                    ref_file
                )
                return

            reference_df = pd.read_parquet(ref_file)
            self.reference_data = reference_df.sample(n=min(10000, len(reference_df)), random_state=42)
            self.logger.info("Loaded reference data: %s", self.reference_data.shape)

        except Exception as e:
            self.logger.error("Failed to load reference data: %s", e)
            self.reference_data = None

    def add_prediction(self, features: Dict, prediction: int, probability: float):
        if not features:
            return

        self.production_buffer.append(features.copy())

        if len(self.production_buffer) >= self.max_buffer_size:
            self.logger.info("Buffer full (%d). Saving production data.", self.max_buffer_size)
            self.save_production_data()
            self.production_buffer = []

    def get_drift_status(self) -> Dict:
        return {
            'reference_data_loaded': self.reference_data is not None,
            'buffer_size': len(self.production_buffer),
            'max_buffer_size': self.max_buffer_size,
        }

    def save_production_data(self):
        if len(self.production_buffer) == 0:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.drift_data_dir / f"production_data_{timestamp}.parquet"

        try:
            df = pd.DataFrame(self.production_buffer)

            # Parquet doesn't support bool columns — convert to int
            for col in df.columns:
                if df[col].dtype == bool or df[col].dtype == 'bool':
                    df[col] = df[col].astype(int)
                elif df[col].dtype == object:
                    try:
                        if df[col].dropna().isin([True, False]).all():
                            df[col] = df[col].astype(int)
                    except (ValueError, TypeError):
                        pass

            df.to_parquet(output_file, index=False)
            self.logger.info("Saved %d production samples to %s", len(df), output_file)
        except Exception as e:
            self.logger.error("Failed to save production data: %s", e)


drift_detector = DriftDetector()
