#!/usr/bin/env python3
"""
Train Battle Winner Prediction Model - Production Script
=========================================================

ML training pipeline for Pokémon battle winner prediction.

Pipeline Steps:
    1. Load train/test datasets (parquet format)
    2. Feature engineering (encoding, derived features, normalization)
    3. Train XGBoost classifier with optional GridSearchCV
    4. Export versioned model, scalers, and metadata

Features:
    - Scenario filtering support (via `scenario_type` column if present)
    - Optional GridSearchCV for hyperparameter tuning (--use-gridsearch)
    - Artifact versioning via --version flag (default: v1)
    - Comprehensive metrics logging (accuracy, precision, recall, F1, AUC)

Usage:
    # Train with default settings
    python machine_learning/train_model.py

    # Train with GridSearch and specific scenario
    python machine_learning/train_model.py --use-gridsearch --version v2 --scenario-type worst_case

    # Train on all scenarios combined
    python machine_learning/train_model.py --version v2 --scenario-type all

Output Artifacts:
    - models/battle_winner_model_<version>.pkl - Trained XGBoost model
    - models/battle_winner_scalers_<version>.pkl - Feature scalers
    - models/battle_winner_metadata_<version>.pkl - Model metadata
"""

import argparse
import pickle
import sys
from datetime import datetime
from pathlib import Path

import joblib  # For RandomForest compression
import pandas as pd
import xgboost as xgb
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.preprocessing import StandardScaler

# MLflow Model Registry
try:
    from machine_learning.mlflow_integration import MLflowTracker
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    print("⚠️  MLflow not available, Model Registry disabled")

# Import new centralized modules (refactored for clean code)
from machine_learning.config import (
    XGBOOST_PARAMS,
    XGBOOST_PARAM_GRID_FAST,
    XGBOOST_PARAM_GRID_EXTENDED,
    RANDOM_SEED,
)
from machine_learning.constants import (
    PROJECT_ROOT,
    MODELS_DIR,
    get_data_dir,
    get_processed_dir,
    get_features_dir,
)
from machine_learning.features import PokemonFeatureEngineer
from machine_learning.evaluation import evaluate_model
from machine_learning.export import export_model, export_features

# Add project root to path
sys.path.insert(0, str(PROJECT_ROOT))

# Global paths (set by main based on args) - kept for backward compatibility
DATA_DIR = None
PROCESSED_DIR = None
FEATURES_DIR = None

# Note: RANDOM_SEED, XGBOOST_PARAMS, XGBOOST_PARAM_GRID_FAST/EXTENDED, MODELS_DIR
# and PROJECT_ROOT are now imported from config.py and constants.py


def load_datasets(dataset_version='v1'):
    """Load train and test datasets from parquet files.

    Args:
        dataset_version: 'v1' for original datasets, 'v2' for multi-scenario datasets
    """
    print(f"Loading datasets (version: {dataset_version})...")

    train_path = PROCESSED_DIR / "train.parquet"
    test_path = PROCESSED_DIR / "test.parquet"

    if not train_path.exists():
        v1_script = "build_battle_winner_dataset.py"
        v2_script = "build_battle_winner_dataset_v2.py"
        script = v2_script if dataset_version == 'v2' else v1_script
        raise FileNotFoundError(
            f"Train dataset not found: {train_path}\n"
            f"Please run: POSTGRES_HOST=localhost python machine_learning/{script}"
        )

    if not test_path.exists():
        raise FileNotFoundError(f"Test dataset not found: {test_path}")

    df_train = pd.read_parquet(train_path)
    df_test = pd.read_parquet(test_path)

    print(f"  Train: {len(df_train):,} samples")
    print(f"  Test: {len(df_test):,} samples")

    # Check for scenario_type column
    if 'scenario_type' in df_train.columns:
        print(f"  ✅ Multi-scenario dataset detected")
        scenario_counts = df_train['scenario_type'].value_counts()
        for scenario, count in scenario_counts.items():
            print(f"     {scenario}: {count:,} samples")
    else:
        print(f"  ℹ️  Single scenario dataset (v1 format)")

    return df_train, df_test


def filter_by_scenario(df_train, df_test, scenario_type: str):
    """
    Optionally filter datasets by scenario_type column if present.

    Args:
        df_train: training dataframe
        df_test: test dataframe
        scenario_type: scenario to keep; "all" keeps everything
    """
    if scenario_type == "all":
        return df_train, df_test

    if "scenario_type" not in df_train.columns:
        print(f"⚠️  scenario_type filtering skipped: column missing (requested '{scenario_type}').")
        return df_train, df_test

    before_train = len(df_train)
    before_test = len(df_test)

    df_train_filtered = df_train[df_train["scenario_type"] == scenario_type]
    df_test_filtered = df_test[df_test["scenario_type"] == scenario_type]

    if df_train_filtered.empty or df_test_filtered.empty:
        print(f"⚠️  scenario_type='{scenario_type}' produced empty split; fallback to full dataset.")
        return df_train, df_test

    print(
        f"✅ Filtering scenario_type='{scenario_type}': "
        f"train {before_train:,}→{len(df_train_filtered):,}, test {before_test:,}→{len(df_test_filtered):,}"
    )

    # Show class balance after filtering
    train_balance = df_train_filtered['winner'].mean()
    test_balance = df_test_filtered['winner'].mean()
    print(f"   Class balance - Train: A={train_balance*100:.1f}% / B={100-train_balance*100:.1f}%")
    print(f"   Class balance - Test:  A={test_balance*100:.1f}% / B={100-test_balance*100:.1f}%")

    return df_train_filtered, df_test_filtered


# ================================================================
# NOTE: engineer_features() function has been REFACTORED
# Now uses PokemonFeatureEngineer class from machine_learning.features.engineering
# This eliminates 145+ lines of duplicated code. See machine_learning/features/engineering.py
# ================================================================


def train_xgboost(X_train, y_train, use_gridsearch: bool = False, grid_type: str = 'fast'):
    """
    Train XGBoost classifier with optional GridSearchCV.

    Args:
        X_train: Training features
        y_train: Training labels
        use_gridsearch: Whether to use GridSearchCV for hyperparameter tuning
        grid_type: 'fast' or 'extended' - which parameter grid to use

    Returns:
        (model, best_params): Trained model and best parameters found
    """
    if use_gridsearch:
        # Select parameter grid
        if grid_type == 'extended':
            param_grid = XGBOOST_PARAM_GRID_EXTENDED
            num_combinations = (len(param_grid['n_estimators']) * len(param_grid['max_depth']) *
                                len(param_grid['learning_rate']) * len(param_grid['subsample']) *
                                len(param_grid['colsample_bytree']))
            print(f"\n🔍 Training XGBoost with GridSearchCV (EXTENDED grid: {num_combinations} combinations)...")
        else:
            param_grid = XGBOOST_PARAM_GRID_FAST
            num_combinations = (len(param_grid['n_estimators']) * len(param_grid['max_depth']) *
                                len(param_grid['learning_rate']))
            print(f"\n🔍 Training XGBoost with GridSearchCV (FAST grid: {num_combinations} combinations)...")

        cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=RANDOM_SEED)
        base_model = xgb.XGBClassifier(
            random_state=RANDOM_SEED,
            n_jobs=-1,
            eval_metric='logloss',
            tree_method='hist',          # CPU-optimized
            predictor='cpu_predictor'    # Explicit CPU
        )
        grid = GridSearchCV(
            estimator=base_model,
            param_grid=param_grid,
            scoring="roc_auc",
            cv=cv,
            n_jobs=-1,                   # Parallelize across all cores
            verbose=1,
            return_train_score=False,    # Don't compute train scores (faster)
        )
        grid.fit(X_train, y_train)
        print(f"  ✅ Best params: {grid.best_params_}")
        print(f"  ✅ Best CV ROC-AUC: {grid.best_score_:.4f}")
        best_model = grid.best_estimator_
        best_params = grid.best_params_
    else:
        print("\n🚀 Training XGBoost model (fixed params)...")
        print(f"  Hyperparameters: {XGBOOST_PARAMS}")

        # Split for early stopping
        from sklearn.model_selection import train_test_split
        X_tr, X_val, y_tr, y_val = train_test_split(
            X_train, y_train, test_size=0.2, random_state=RANDOM_SEED, stratify=y_train
        )

        best_model = xgb.XGBClassifier(**XGBOOST_PARAMS)
        best_model.fit(
            X_tr, y_tr,
            eval_set=[(X_tr, y_tr), (X_val, y_val)],
            verbose=False
        )
        best_params = XGBOOST_PARAMS

        # Report best iteration
        if hasattr(best_model, 'best_iteration'):
            print(f"  ✅ Best iteration: {best_model.best_iteration}/{best_model.n_estimators}")

    print("  ✅ Training complete")
    return best_model, best_params


# Note: evaluate_model, export_model, and export_features are now imported
#       from machine_learning.evaluation and machine_learning.export


def main():
    """Main training pipeline."""
    parser = argparse.ArgumentParser(
        description="Train Battle Winner Prediction Model (Production)"
    )
    parser.add_argument(
        '--skip-export-features',
        action='store_true',
        help='Skip exporting feature-engineered datasets'
    )
    parser.add_argument(
        '--use-gridsearch',
        action='store_true',
        help='Enable small GridSearchCV to tune XGBoost hyperparameters'
    )
    parser.add_argument(
        '--version',
        default='v1',
        help='Suffix for exported artifacts (e.g., v2)'
    )
    parser.add_argument(
        '--scenario-type',
        default='all',
        help="Filter dataset by scenario_type column if present (e.g., best_move, random_move, all_combinations)."
    )
    parser.add_argument(
        '--dataset-version',
        choices=['v1', 'v2'],
        default='v1',
        help="Dataset version: v1 (original) or v2 (multi-scenario)"
    )
    parser.add_argument(
        '--grid-type',
        choices=['fast', 'extended'],
        default='fast',
        help="GridSearch parameter grid: fast (for CI) or extended (for notebooks)"
    )
    parser.add_argument(
        '--no-mlflow',
        action='store_true',
        help="Disable MLflow Model Registry registration"
    )
    args = parser.parse_args()

    # Set global paths based on dataset version (using helper functions from constants.py)
    global DATA_DIR, PROCESSED_DIR, FEATURES_DIR
    DATA_DIR = get_data_dir(args.dataset_version)
    PROCESSED_DIR = get_processed_dir(args.dataset_version)
    FEATURES_DIR = get_features_dir(args.dataset_version)

    print("=" * 70)
    print("BATTLE WINNER PREDICTION MODEL - TRAINING")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Random Seed: {RANDOM_SEED}")
    print(f"Dataset Version: {args.dataset_version}")
    print(f"Model Version: {args.version}")
    print(f"Scenario Filter: {args.scenario_type}")
    print(f"GridSearch: {'enabled' if args.use_gridsearch else 'disabled'}")
    if args.use_gridsearch:
        print(f"Grid Type: {args.grid_type}")

    try:
        # Load data
        df_train, df_test = load_datasets(dataset_version=args.dataset_version)

        # Optional scenario filtering
        df_train, df_test = filter_by_scenario(df_train, df_test, args.scenario_type)

        # Feature engineering (using refactored class)
        feature_engineer = PokemonFeatureEngineer()
        X_train, X_test, y_train, y_test, scalers, feature_columns = feature_engineer.fit_transform(
            df_train, df_test
        )

        # Train model
        model, best_params = train_xgboost(
            X_train, y_train, use_gridsearch=args.use_gridsearch, grid_type=args.grid_type)

        # Evaluate
        metrics = evaluate_model(model, X_train, X_test, y_train, y_test, model_name="XGBoost", verbose=True)

        # Export model artifacts
        model_path = export_model(
            model,
            scalers,
            feature_columns,
            metrics,
            hyperparams=best_params,
            version=args.version,
            verbose=True,
        )

        # Register in MLflow Model Registry
        if MLFLOW_AVAILABLE and model_path and not args.no_mlflow:
            try:
                tracker = MLflowTracker(experiment_name=f"battle_winner_{args.version}")
                tracker.start_run(run_name=f"train_model_{args.version}_{datetime.now().strftime('%Y%m%d_%H%M')}")

                # Log parameters
                tracker.log_params({
                    'dataset_version': args.dataset_version,
                    'model_version': args.version,
                    'scenario_type': args.scenario_type or 'all',
                    'use_gridsearch': args.use_gridsearch,
                    'grid_type': args.grid_type if args.use_gridsearch else 'none',
                    **(best_params if best_params else {})
                })

                # Log metrics
                tracker.log_metrics(metrics)

                # Log model with scalers and metadata
                tracker.log_model(model, artifact_path=f"model_{args.version}",
                                  model_type='xgboost', scalers=scalers,
                                  metadata={'feature_columns': feature_columns})

                # Register in Model Registry
                model_name = "battle_winner_predictor"
                description = f"XGBoost model v{args.version} - Accuracy: {metrics['test_accuracy']:.4f}"
                if args.use_gridsearch:
                    description += f" (GridSearch {args.grid_type})"

                version_number = tracker.register_model(model_name=model_name, description=description)

                # Auto-promote to Production if quality threshold met
                if version_number and metrics.get('test_accuracy', 0) >= 0.85:
                    print(f"\n🎯 Model meets quality threshold (accuracy >= 0.85)")
                    tracker.promote_to_production(model_name, version_number)
                    print(f"✅ Model promoted to Production stage in MLflow Registry")
                elif version_number:
                    print(f"\n⚠️  Model registered as version {version_number} but not promoted (accuracy < 0.85)")
                    print(f"   Manual promotion: MLflow UI or CLI")

                tracker.end_run()
                print(f"\n✅ Model registered in MLflow Model Registry")
            except Exception as e:
                print(f"\n⚠️  MLflow registration failed: {e}")

        # Export features (optional)
        if not args.skip_export_features:
            export_features(X_train, X_test, y_train, y_test, FEATURES_DIR, verbose=True)

        print("\n" + "=" * 70)
        print("✅ TRAINING COMPLETE")
        print("=" * 70)
        print(f"\n📊 Test Accuracy: {metrics['test_accuracy']*100:.2f}%")
        print(f"📊 Test ROC-AUC: {metrics['test_roc_auc']:.4f}")

    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
