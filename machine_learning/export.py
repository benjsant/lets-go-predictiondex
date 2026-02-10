"""
Model export module for Pokemon battle prediction.

This module provides functions for exporting trained models, scalers,
and feature-engineered datasets with proper versioning and metadata.

Validation: C13 (model packaging and MLOps)
"""

import json
import pickle
from datetime import datetime
from typing import Any, Dict, List, Optional

import joblib
import pandas as pd

from machine_learning.config import RANDOM_SEED
from machine_learning.constants import MODELS_DIR


def export_model(model: Any, scalers: Dict, feature_columns: List[str],
                 metrics: Dict, *, hyperparams: Optional[Dict] = None,
                 version: str = "v1", verbose: bool = True):
    """
    Export trained model, scalers, and metadata.

    This function handles the complete export process including:
    - Model serialization (with compression for RandomForest)
    - Scaler serialization
    - Metadata export (both pickle and JSON formats)

    Args:
        model: Trained model to export
        scalers: Dictionary containing fitted scalers
        feature_columns: List of feature column names
        metrics: Dictionary of evaluation metrics
        hyperparams: Optional dictionary of hyperparameters used for training
        version: Version string for file naming (e.g., 'v1', 'v2')
        verbose: Whether to print export progress

    Returns:
        Path to the exported model file as string

    Validation: C13 (model packaging)
    """
    if verbose:
        print("\n" + "=" * 80)
        print("STEP 6: MODEL EXPORT")
        print("=" * 80)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # Export model (use joblib compression for RandomForest, pickle for others)
    model_path = MODELS_DIR / f"battle_winner_model_{version}.pkl"
    model_type_name = type(model).__name__

    if model_type_name == 'RandomForestClassifier':
        # Use joblib with aggressive compression for RandomForest (5-10x smaller)
        joblib.dump(model, model_path, compress=('zlib', 9))
        if verbose:
            print(f"\n✅ Model exported (joblib compressed): {model_path}")
    else:
        # XGBoost and others use standard pickle
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        if verbose:
            print(f"\n✅ Model exported: {model_path}")

    # Export scalers
    scalers_path = MODELS_DIR / f"battle_winner_scalers_{version}.pkl"
    with open(scalers_path, 'wb') as f:
        pickle.dump(scalers, f)
    if verbose:
        print(f"✅ Scalers exported: {scalers_path}")

    # Export metadata
    metadata = {
        'model_type': type(model).__name__,
        'version': version,
        'trained_at': datetime.now().isoformat(),
        'feature_columns': feature_columns,
        'n_features': len(feature_columns),
        'hyperparameters': hyperparams or {},
        'metrics': metrics,
        'random_seed': RANDOM_SEED,
    }

    metadata_path = MODELS_DIR / f"battle_winner_metadata_{version}.pkl"
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)
    if verbose:
        print(f"✅ Metadata exported: {metadata_path}")

    # Export metadata as JSON for readability
    metadata_json = metadata.copy()
    metadata_json['feature_columns'] = feature_columns[:10] + ['...'] if len(feature_columns) > 10 else feature_columns

    metadata_json_path = MODELS_DIR / f"battle_winner_metadata_{version}.json"
    with open(metadata_json_path, 'w', encoding='utf-8') as f:
        json.dump(metadata_json, f, indent=2)
    if verbose:
        print(f"✅ Metadata (JSON) exported: {metadata_json_path}")
        print(f"\n✅ All artifacts exported to: {MODELS_DIR}")

    return str(model_path)  # Return path for MLflow logging


def export_features(X_train: pd.DataFrame, X_test: pd.DataFrame,
                    y_train: pd.Series, y_test: pd.Series,
                    features_dir, verbose: bool = True):
    """
    Export feature-engineered datasets for reproducibility.

    This function saves the processed training and test datasets in Parquet format,
    which allows for efficient storage and fast loading while preserving data types.

    Args:
        X_train: Training features DataFrame
        X_test: Test features DataFrame
        y_train: Training labels Series
        y_test: Test labels Series
        features_dir: Directory path where features should be saved
        verbose: Whether to print export progress

    Note:
        Uses PyArrow Parquet format for efficient storage and type preservation.
    """
    if verbose:
        print("\nExporting feature-engineered datasets...")

    features_dir.mkdir(parents=True, exist_ok=True)

    X_train.to_parquet(features_dir / "X_train.parquet", index=False, engine='pyarrow')
    X_test.to_parquet(features_dir / "X_test.parquet", index=False, engine='pyarrow')
    y_train.to_frame('winner').to_parquet(features_dir / "y_train.parquet", index=False, engine='pyarrow')
    y_test.to_frame('winner').to_parquet(features_dir / "y_test.parquet", index=False, engine='pyarrow')

    if verbose:
        print(f"✅ Features exported to: {features_dir}")
