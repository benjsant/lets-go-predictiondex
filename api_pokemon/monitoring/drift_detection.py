"""
Production Data Collector
==========================

Collects ML predictions for future analysis and model retraining.
Stores prediction features and outcomes in parquet files.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd


class DriftDetector:
    """
    Singleton class for collecting production prediction data.

    Collects ML features and predictions from production traffic
    and periodically saves them for future analysis, drift detection,
    or model retraining.
    """

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

        # Directories
        self.monitoring_dir = Path(__file__).parent
        self.drift_data_dir = self.monitoring_dir / "drift_data"

        # Create directories
        self.drift_data_dir.mkdir(parents=True, exist_ok=True)

        # Production data buffer
        self.production_buffer: List[Dict] = []
        self.max_buffer_size = 100  # Save every 100 predictions

        # Reference data (for future drift detection if needed)
        self.reference_data: Optional[pd.DataFrame] = None
        self._load_reference_data()

    def _load_reference_data(self):
        """
        Load reference data from training set.

        Samples 10,000 examples from X_train.parquet for future drift analysis.
        """
        try:
            # Try to load from data/datasets/
            ref_file = Path("data/datasets/X_train.parquet")
            if not ref_file.exists():
                # Try from Docker mount point
                ref_file = Path("/app/data/datasets/X_train.parquet")

            if not ref_file.exists():
                self.logger.warning(
                    "Reference data file not found: %s. "
                    "This is optional for production data collection.",
                    ref_file
                )
                return

            # Load and sample reference data
            reference_df = pd.read_parquet(ref_file)
            self.reference_data = reference_df.sample(n=min(10000, len(reference_df)), random_state=42)
            self.logger.info("Loaded reference data: %s", self.reference_data.shape)

        except Exception as e:
            self.logger.error("Failed to load reference data: %s", e)
            self.reference_data = None

    def add_prediction(
        self,
        features: Dict,
        prediction: int,
        probability: float
    ):
        """
        Add a new prediction to the production buffer.

        Args:
            features: Dictionary of ML input features (133 features)
            prediction: Predicted class (0 or 1)
            probability: Prediction probability
        """
        if not features:
            return

        # Store ML features for future analysis
        self.production_buffer.append(features.copy())

        # Save buffer when it reaches max size
        if len(self.production_buffer) >= self.max_buffer_size:
            self.logger.info("Buffer full (%d). Saving production data.", self.max_buffer_size)
            self.save_production_data()
            self.production_buffer = []

    def get_drift_status(self) -> Dict:
        """
        Get current buffer status.

        Returns:
            Dictionary with current buffer metrics
        """
        return {
            'reference_data_loaded': self.reference_data is not None,
            'buffer_size': len(self.production_buffer),
            'max_buffer_size': self.max_buffer_size,
        }

    def save_production_data(self):
        """
        Save production buffer to parquet file.

        Useful for future drift detection, model retraining, and analysis.
        """
        if len(self.production_buffer) == 0:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.drift_data_dir / f"production_data_{timestamp}.parquet"

        try:
            df = pd.DataFrame(self.production_buffer)

            # Convert all object/boolean columns to appropriate types for parquet
            # One-hot encoded features are stored as booleans by the ML model
            for col in df.columns:
                # Check if column contains boolean values
                if df[col].dtype == bool or df[col].dtype == 'bool':
                    df[col] = df[col].astype(int)
                elif df[col].dtype == object:
                    # Try to convert object columns that might contain booleans
                    try:
                        # If all values are True/False, convert to int
                        if df[col].dropna().isin([True, False]).all():
                            df[col] = df[col].astype(int)
                    except (ValueError, TypeError):
                        pass  # Keep as object if conversion fails

            df.to_parquet(output_file, index=False)
            self.logger.info("Saved %d production samples to %s", len(df), output_file)
        except Exception as e:
            self.logger.error("Failed to save production data: %s", e)


# Singleton instance
drift_detector = DriftDetector()
