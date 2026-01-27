"""
Data Drift Detection using Evidently AI 0.7
===========================================

Detects distribution shifts in model inputs and predictions.
Generates periodic drift reports and alerts.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

try:
    from evidently import DataDefinition, Dataset, Report
    from evidently.presets import DataDriftPreset
except ImportError:
    raise ImportError(
        "Evidently AI is not installed. "
        "Install it with: pip install 'evidently>=0.7.0,<0.8.0'"
    )


class DriftDetector:
    """
    Singleton class for drift detection using Evidently AI 0.7.x

    Uses a reference dataset from training data to detect distribution shifts
    in production predictions. Generates periodic HTML and JSON reports.
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
        self.drift_reports_dir = self.monitoring_dir / "drift_reports"
        self.drift_data_dir = self.monitoring_dir / "drift_data"

        # Create directories
        self.drift_reports_dir.mkdir(parents=True, exist_ok=True)
        self.drift_data_dir.mkdir(parents=True, exist_ok=True)

        # Reference data (Evidently Dataset)
        self.reference_data: Optional[Dataset] = None
        self.production_buffer: List[Dict] = []
        self.max_buffer_size = 1000
        self.report_frequency = timedelta(hours=1)
        self.last_report_time = datetime.now()

        # Data definition for Evidently 0.7
        self.data_definition = DataDefinition()

        # Load reference data from training set
        self._load_reference_data()

    def _load_reference_data(self):
        """
        Load reference data from training set.

        Samples 10,000 examples from X_train.parquet for drift comparison.
        """
        try:
            # Try to load from data/datasets/
            ref_file = Path("data/datasets/X_train.parquet")
            if not ref_file.exists():
                # Try from Docker mount point
                ref_file = Path("/app/data/datasets/X_train.parquet")

            if not ref_file.exists():
                self.logger.warning(
                    f"Reference data file not found: {ref_file}. "
                    "Drift detection will be disabled until training data is available."
                )
                return

            # Load and sample reference data
            reference_df = pd.read_parquet(ref_file)
            sampled_df = reference_df.sample(n=min(10000, len(reference_df)), random_state=42)

            # Create Evidently Dataset from pandas DataFrame
            self.reference_data = Dataset.from_pandas(
                sampled_df,
                data_definition=self.data_definition
            )
            self.logger.info(f"Loaded reference data: {sampled_df.shape}")

        except Exception as e:
            self.logger.error(f"Failed to load reference data: {e}")
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
            features: Dictionary of input features
            prediction: Predicted class (0 or 1)
            probability: Prediction probability
        """
        if self.reference_data is None:
            # Drift detection disabled without reference data
            return

        # Add metadata
        prediction_data = {
            **features,
            'predicted_winner': prediction,
            'win_probability': probability,
            'timestamp': datetime.now().isoformat()
        }

        self.production_buffer.append(prediction_data)

        # Check if buffer is full
        if len(self.production_buffer) >= self.max_buffer_size:
            self.logger.info(f"Buffer full ({self.max_buffer_size}). Saving production data.")
            self.save_production_data()
            self.production_buffer = []

        # Check if it's time to generate a report
        if datetime.now() - self.last_report_time >= self.report_frequency:
            if len(self.production_buffer) > 0:
                self.generate_drift_report()

    def generate_drift_report(self) -> Dict:
        """
        Generate drift report using Evidently AI 0.7.

        Compares production data buffer against reference dataset.
        Saves HTML dashboard and JSON report.

        Returns:
            Dictionary with drift summary metrics
        """
        if self.reference_data is None:
            self.logger.warning("Cannot generate drift report: no reference data loaded")
            return {}

        if len(self.production_buffer) == 0:
            self.logger.info("No production data to analyze for drift")
            return {}

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            # Create DataFrame from buffer
            production_df = pd.DataFrame(self.production_buffer)

            # Create Evidently Dataset for production data
            production_dataset = Dataset.from_pandas(
                production_df,
                data_definition=self.data_definition
            )

            # Create and run Evidently Report with DataDriftPreset
            report = Report([DataDriftPreset()])
            report.run(production_dataset, self.reference_data)

            # Save report as JSON
            report_file = self.drift_reports_dir / f"drift_report_{timestamp}.json"

            # Save as JSON
            with open(report_file, 'w') as f:
                f.write(report.json())

            # Generate HTML dashboard
            dashboard_file = self.drift_reports_dir / f"drift_dashboard_{timestamp}.html"
            report.save_html(str(dashboard_file))

            self.logger.info(f"Drift report generated: {dashboard_file}")

            # Extract drift summary from report
            drift_dict = report.as_dict()

            # Navigate the new Evidently 0.7 structure
            metrics_data = drift_dict.get('metrics', [])

            # Find DatasetDriftMetric in metrics list
            drift_result = {}
            for metric in metrics_data:
                if 'DatasetDriftMetric' in str(type(metric)):
                    drift_result = metric.get('result', {})
                    break

            drift_summary = {
                'timestamp': timestamp,
                'n_features': drift_result.get('number_of_columns', 0),
                'n_drifted_features': drift_result.get('number_of_drifted_columns', 0),
                'share_drifted_features': drift_result.get('share_of_drifted_columns', 0),
                'dataset_drift': drift_result.get('dataset_drift', False),
            }

            # Save summary
            summary_file = self.drift_reports_dir / f"drift_summary_{timestamp}.json"
            with open(summary_file, 'w') as f:
                json.dump(drift_summary, f, indent=2)

            # Update last report time
            self.last_report_time = datetime.now()

            self.logger.info(
                f"Drift detected: {drift_summary['n_drifted_features']}/{drift_summary['n_features']} features "
                f"({drift_summary['share_drifted_features']:.1%})"
            )

            return drift_summary

        except Exception as e:
            self.logger.error(f"Failed to generate drift report: {e}", exc_info=True)
            return {}

    def get_drift_status(self) -> Dict:
        """
        Get current drift status summary.

        Returns:
            Dictionary with current drift metrics
        """
        return {
            'reference_data_loaded': self.reference_data is not None,
            'buffer_size': len(self.production_buffer),
            'max_buffer_size': self.max_buffer_size,
            'last_report_time': self.last_report_time.isoformat(),
            'next_report_due': (self.last_report_time + self.report_frequency).isoformat(),
        }

    def save_production_data(self):
        """
        Save production buffer to parquet file.

        Useful for debugging and retraining.
        """
        if len(self.production_buffer) == 0:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.drift_data_dir / f"production_data_{timestamp}.parquet"

        try:
            df = pd.DataFrame(self.production_buffer)
            df.to_parquet(output_file, index=False)
            self.logger.info(f"Saved {len(df)} production samples to {output_file}")
        except Exception as e:
            self.logger.error(f"Failed to save production data: {e}")


# Singleton instance
drift_detector = DriftDetector()
