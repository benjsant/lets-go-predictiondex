#!/usr/bin/env python3
"""
Unified ML Pipeline - Let's Go PredictionDex
==============================================

This script orchestrates the COMPLETE machine learning pipeline:
1. Dataset Preparation (DB → features → train/test split) [v1 or v2 multi-scenarios]
2. Model Training (XGBoost + optional hyperparameter tuning)
3. Model Evaluation (metrics, confusion matrix, ROC curve, feature importance)
4. Model Comparison (compare multiple models)
5. Model Selection (select best based on metrics)
6. Model Export (artifacts + metadata)

Usage:
    # Run complete pipeline (v1 - original)
    python machine_learning/run_machine_learning.py --mode=all

    # Run complete pipeline (v2 - multi-scenarios)
    python machine_learning/run_machine_learning.py --mode=all --dataset-version v2

    # Generate v2 dataset with specific scenario
    python machine_learning/run_machine_learning.py --mode=dataset --dataset-version v2 --scenario-type best_move

    # Generate v2 dataset with all scenarios
    python machine_learning/run_machine_learning.py --mode=dataset --dataset-version v2 --scenario-type all

    # Train on v2 dataset with GridSearch extended (for notebooks)
    python machine_learning/run_machine_learning.py --mode=train --dataset-version v2 --scenario-type all --tune-hyperparams --grid-type extended

    # Run specific steps
    python machine_learning/run_machine_learning.py --mode=train
    python machine_learning/run_machine_learning.py --mode=evaluate
    python machine_learning/run_machine_learning.py --mode=compare

Output (v1):
    - data/ml/battle_winner/raw/matchups.parquet
    - data/ml/battle_winner/processed/train.parquet
    - data/ml/battle_winner/processed/test.parquet
    - models/battle_winner_model_v1.pkl

Output (v2):
    - data/ml/battle_winner_v2/raw/matchups_*.parquet
    - data/ml/battle_winner_v2/processed/train.parquet (with scenario_type column)
    - data/ml/battle_winner_v2/processed/test.parquet (with scenario_type column)
    - models/battle_winner_model_v2.pkl

Validation:
    - Compétence C12: Tests automatisés (dataset validation, preprocessing, training)
    - Compétence C13: MLOps pipeline (orchestration, versioning, export)
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV

# MLflow integration (C13 - MLOps)
try:
    from machine_learning.mlflow_integration import get_mlflow_tracker
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    print("⚠️  MLflow not available - tracking disabled")

# Import new centralized modules (refactored for clean code)
from machine_learning.config import (
    XGBOOST_PARAMS,
    XGBOOST_PARAM_GRID_FAST,
    RANDOM_SEED,
    SAFE_GRIDSEARCH_N_JOBS,
)
from machine_learning.constants import (
    PROJECT_ROOT,
    MODELS_DIR,
    get_data_dir,
    get_raw_dir,
    get_processed_dir,
    get_features_dir,
)
from machine_learning.features import PokemonFeatureEngineer
from machine_learning.evaluation import (
    evaluate_model,
    analyze_feature_importance,
    compare_models,
)
from machine_learning.export import export_model, export_features

# Add project root to path
sys.path.insert(0, str(PROJECT_ROOT))

# Global paths (set by main based on args) - kept for backward compatibility
DATA_DIR = None
RAW_DIR = None
PROCESSED_DIR = None
FEATURES_DIR = None

# Backward compatibility aliases (using new config system)
DEFAULT_XGBOOST_PARAMS = XGBOOST_PARAMS
XGBOOST_PARAM_GRID = XGBOOST_PARAM_GRID_FAST  # Default to fast grid

# RandomForest params (kept as-is, not refactored yet)
DEFAULT_RF_PARAMS = {
    'n_estimators': 50,
    'max_depth': 12,
    'min_samples_split': 10,
    'min_samples_leaf': 4,
    'random_state': RANDOM_SEED,
    'n_jobs': -1,
}


# ================================================================
# STEP 1: DATASET PREPARATION
# ================================================================

def run_dataset_preparation(dataset_version: str = 'v1', scenario_type: str = 'all',
                            num_random_samples: int = 5, max_combinations: int = 20,
                            verbose: bool = True) -> bool:
    """
    Run dataset preparation script to generate train/test datasets from DB.

    Args:
        dataset_version: 'v1' (original) or 'v2' (multi-scenarios)
        scenario_type: For v2 - 'best_move', 'random_move', 'all_combinations', or 'all'
        num_random_samples: For v2 random_move - number of samples per matchup
        max_combinations: For v2 all_combinations - max combinations per matchup
        verbose: Print detailed output

    Validation: C12 (dataset quality checks)
    """
    if verbose:
        print("\n" + "=" * 80)
        print("STEP 1: DATASET PREPARATION")
        print("=" * 80)
        print(f"\nGenerating Pokemon battle datasets (version: {dataset_version})...")
        if dataset_version == 'v2':
            print(f"Scenario type: {scenario_type}")

    try:
        # Select script based on version
        if dataset_version == 'v2':
            script_name = "build_battle_winner_dataset_v2.py"
            cmd = [
                sys.executable,
                str(PROJECT_ROOT / "machine_learning" / script_name),
                "--scenario-type", scenario_type,
                "--num-random-samples", str(num_random_samples),
                "--max-combinations", str(max_combinations)
            ]
        else:
            script_name = "build_battle_winner_dataset.py"
            cmd = [
                sys.executable,
                str(PROJECT_ROOT / "machine_learning" / script_name)
            ]

        # Run dataset generation
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            env={**os.environ, "POSTGRES_HOST": os.getenv("POSTGRES_HOST", "localhost")}
        )

        if verbose:
            print(result.stdout)

        # Validate output files
        train_path = PROCESSED_DIR / "train.parquet"
        test_path = PROCESSED_DIR / "test.parquet"

        if not train_path.exists():
            raise FileNotFoundError(f"Train dataset not created: {train_path}")
        if not test_path.exists():
            raise FileNotFoundError(f"Test dataset not created: {test_path}")

        # Validate dataset quality
        df_train = pd.read_parquet(train_path)
        df_test = pd.read_parquet(test_path)

        if verbose:
            print("\n✅ Dataset validation:")
            print(f"   Train samples: {len(df_train):,}")
            print(f"   Test samples: {len(df_test):,}")
            print(f"   Total features: {df_train.shape[1]}")

            # Check for scenario_type column (v2)
            if 'scenario_type' in df_train.columns:
                print(f"\n   ✅ Multi-scenario dataset (v2) detected:")
                scenario_counts = df_train['scenario_type'].value_counts()
                for scenario, count in scenario_counts.items():
                    print(f"      {scenario}: {count:,} samples")

            # Check class balance
            train_balance = df_train['winner'].value_counts(normalize=True)
            print(f"\n   Class balance (train):")
            print(f"     Winner A: {train_balance.get(1, 0)*100:.1f}%")
            print(f"     Winner B: {train_balance.get(0, 0)*100:.1f}%")

            # Check for nulls
            null_count = df_train.isnull().sum().sum()
            if null_count > 0:
                print(f"\n   ⚠️  Warning: {null_count} null values detected")
            else:
                print(f"\n   ✓ No null values")

        return True

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Dataset preparation failed:")
        print(e.stderr)
        return False


def filter_by_scenario(df_train: pd.DataFrame, df_test: pd.DataFrame, scenario_type: str, verbose: bool = True):
    """
    Optionally filter datasets by scenario_type column if present.
    Args:
        df_train: training dataframe
        df_test: test dataframe
        scenario_type: scenario to keep; "all" keeps everything
    Returns:
        df_train_filtered, df_test_filtered
    """
    if scenario_type == "all":
        return df_train, df_test

    try:
        if "scenario_type" not in df_train.columns:
            if verbose:
                print(f"⚠️  scenario_type filtering skipped: column missing (requested '{scenario_type}').")
            return df_train, df_test

        before_train = len(df_train)
        before_test = len(df_test)

        df_train_filtered = df_train[df_train["scenario_type"] == scenario_type]
        df_test_filtered = df_test[df_test["scenario_type"] == scenario_type]

        if df_train_filtered.empty or df_test_filtered.empty:
            if verbose:
                print(f"⚠️  scenario_type='{scenario_type}' produced empty split; fallback to full dataset.")
            return df_train, df_test

        if verbose:
            print(
                f"Filtering scenario_type='{scenario_type}': "
                f"train {before_train}→{len(df_train_filtered)}, test {before_test}→{len(df_test_filtered)}"
            )
        return df_train_filtered, df_test_filtered

    except Exception as e:
        print(f"\n❌ Error during scenario filtering: {e}")
        return df_train, df_test


# ================================================================
# STEP 2: FEATURE ENGINEERING
# ================================================================
# NOTE: engineer_features() function has been REFACTORED
# Now uses PokemonFeatureEngineer class from machine_learning.features.engineering
# This eliminates 140+ lines of duplicated code between run_machine_learning.py
# and train_model.py. See machine_learning/features/engineering.py for implementation.
# ================================================================


# ================================================================
# STEP 3: MODEL TRAINING
# ================================================================

def train_model(X_train: pd.DataFrame, y_train: pd.Series,
                model_type: str = 'xgboost',
                hyperparams: Optional[Dict] = None,
                verbose: bool = True) -> Any:
    """
    Train a classification model.

    Validation: C12 (training pipeline tests)

    Args:
        X_train: Training features
        y_train: Training target
        model_type: 'xgboost' or 'random_forest'
        hyperparams: Custom hyperparameters (optional)
        verbose: Print training progress

    Returns:
        Trained model
    """
    if verbose:
        print("\n" + "=" * 80)
        print(f"STEP 3: MODEL TRAINING ({model_type.upper()})")
        print("=" * 80)

    if model_type == 'xgboost':
        params = hyperparams or DEFAULT_XGBOOST_PARAMS
        if verbose:
            print(f"\nHyperparameters: {params}")
        model = xgb.XGBClassifier(**params)

    elif model_type == 'random_forest':
        params = hyperparams or DEFAULT_RF_PARAMS
        if verbose:
            print(f"\nHyperparameters: {params}")
        model = RandomForestClassifier(**params)

    else:
        raise ValueError(f"Unsupported model_type: {model_type}")

    if verbose:
        print("\nTraining model...")

    # Training with early stopping for XGBoost
    if model_type == 'xgboost':
        # Split train into train/validation for early stopping
        from sklearn.model_selection import train_test_split
        X_tr, X_val, y_tr, y_val = train_test_split(
            X_train, y_train, test_size=0.2, random_state=RANDOM_SEED, stratify=y_train
        )

        # Fit with early stopping
        model.fit(
            X_tr, y_tr,
            eval_set=[(X_tr, y_tr), (X_val, y_val)],
            verbose=False
        )

        if verbose:
            # Get best iteration
            best_iteration = model.best_iteration if hasattr(model, 'best_iteration') else model.n_estimators
            print(f"  Best iteration: {best_iteration}/{model.n_estimators}")
    else:
        # RandomForest doesn't support early stopping
        model.fit(X_train, y_train)

    if verbose:
        print("✅ Training complete")

    return model


def tune_hyperparameters(X_train: pd.DataFrame, y_train: pd.Series,
                         model_type: str = 'xgboost',
                         verbose: bool = True) -> Tuple[Any, Dict]:
    """
    Hyperparameter tuning with GridSearchCV.

    Validation: C12 (model selection tests)

    Args:
        X_train: Training features
        y_train: Training target
        model_type: 'xgboost' or 'random_forest'
        verbose: Print tuning progress

    Returns:
        best_model, best_params
    """
    if verbose:
        print("\n" + "=" * 80)
        print("HYPERPARAMETER TUNING")
        print("=" * 80)
        print(f"\nModel: {model_type}")
        print("Method: GridSearchCV with 3-fold CV")

    if model_type == 'xgboost':
        base_model = xgb.XGBClassifier(random_state=RANDOM_SEED, n_jobs=SAFE_GRIDSEARCH_N_JOBS)
        param_grid = XGBOOST_PARAM_GRID
    else:
        raise ValueError("Hyperparameter tuning only implemented for XGBoost")

    if verbose:
        print(f"\nParameter grid:")
        for param, values in param_grid.items():
            print(f"  {param}: {values}")

        total_combinations = np.prod([len(v) for v in param_grid.values()])
        print(f"\nTotal combinations: {total_combinations}")
        print("This may take a while...\n")

    # Configure GridSearchCV with optimization
    from sklearn.model_selection import StratifiedKFold
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=RANDOM_SEED)

    grid_search = GridSearchCV(
        estimator=base_model,
        param_grid=param_grid,
        cv=cv,
        scoring='roc_auc',      # Better metric for imbalanced data
        n_jobs=SAFE_GRIDSEARCH_N_JOBS,  # Auto-ajusté selon plateforme (Windows/Linux)
        verbose=2 if verbose else 0,
        refit=True,             # Refit best model on full training set
        return_train_score=False  # Don't compute train scores (faster)
    )

    # Fit with evaluation set for monitoring (no early stopping in GridSearchCV directly)
    grid_search.fit(X_train, y_train)

    if verbose:
        print(f"\n✅ Best parameters found:")
        for param, value in grid_search.best_params_.items():
            print(f"   {param}: {value}")
        print(f"\n✅ Best CV accuracy: {grid_search.best_score_:.4f}")

    return grid_search.best_estimator_, grid_search.best_params_


# ================================================================
# STEP 4: MODEL EVALUATION
# ================================================================
# Note: evaluate_model() and analyze_feature_importance() are now imported
#       from machine_learning.evaluation


# ================================================================
# STEP 5: MODEL COMPARISON
# ================================================================
# Note: compare_models() is now imported from machine_learning.evaluation


# ================================================================
# STEP 6: MODEL EXPORT
# ================================================================
# Note: export_model() and export_features() are now imported
#       from machine_learning.export


# ================================================================
# MAIN PIPELINE
# ================================================================

def main():
    """Main ML pipeline orchestration."""
    parser = argparse.ArgumentParser(
        description="Unified ML Pipeline - Let's Go PredictionDex",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run complete pipeline
  python machine_learning/run_machine_learning.py --mode=all

  # Run specific steps
  python machine_learning/run_machine_learning.py --mode=dataset
  python machine_learning/run_machine_learning.py --mode=train
  python machine_learning/run_machine_learning.py --mode=evaluate
  python machine_learning/run_machine_learning.py --mode=compare

  # With hyperparameter tuning
  python machine_learning/run_machine_learning.py --mode=all --tune-hyperparams

  # Skip feature export
  python machine_learning/run_machine_learning.py --mode=all --skip-export-features
        """
    )

    parser.add_argument(
        '--mode',
        type=str,
        choices=['all', 'dataset', 'train', 'evaluate', 'compare'],
        default='all',
        help='Pipeline mode (default: all)'
    )
    parser.add_argument(
        '--tune-hyperparams',
        action='store_true',
        help='Run hyperparameter tuning (slower)'
    )
    parser.add_argument(
        '--skip-export-features',
        action='store_true',
        help='Skip exporting feature-engineered datasets'
    )
    parser.add_argument(
        '--version',
        type=str,
        default='v1',
        help='Suffix for exported artifacts (default: v1)'
    )
    parser.add_argument(
        '--scenario-type',
        type=str,
        default='all',
        help='For v2 datasets: best_move, random_move, all_combinations, or all (default: all)'
    )
    parser.add_argument(
        '--dataset-version',
        type=str,
        choices=['v1', 'v2'],
        default='v1',
        help='Dataset version: v1 (original) or v2 (multi-scenarios) (default: v1)'
    )
    parser.add_argument(
        '--grid-type',
        type=str,
        choices=['fast', 'extended'],
        default='fast',
        help='GridSearch parameter grid: fast (for CI) or extended (for notebooks) (default: fast)'
    )
    parser.add_argument(
        '--num-random-samples',
        type=int,
        default=5,
        help='For v2 random_move scenario: number of samples per matchup (default: 5)'
    )
    parser.add_argument(
        '--max-combinations',
        type=int,
        default=20,
        help='For v2 all_combinations scenario: max combinations per matchup (default: 20)'
    )
    parser.add_argument(
        '--model',
        type=str,
        choices=['xgboost', 'random_forest'],
        default='xgboost',
        help='Model to train (default: xgboost)'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress output (quiet mode)'
    )

    args = parser.parse_args()
    verbose = not args.quiet

    # Set global paths based on dataset version (using helper functions from constants.py)
    global DATA_DIR, RAW_DIR, PROCESSED_DIR, FEATURES_DIR
    DATA_DIR = get_data_dir(args.dataset_version)
    RAW_DIR = get_raw_dir(args.dataset_version)
    PROCESSED_DIR = get_processed_dir(args.dataset_version)
    FEATURES_DIR = get_features_dir(args.dataset_version)

    # Initialize MLflow tracker (C13 - MLOps)
    tracker = None
    if MLFLOW_AVAILABLE:
        try:
            experiment_name = f"pokemon_battle_{args.dataset_version}"
            tracker = get_mlflow_tracker(experiment_name)
            if verbose:
                print(f"\n✅ MLflow tracking enabled: {experiment_name}")
        except Exception as e:
            if verbose:
                print(f"\n⚠️  MLflow tracking disabled: {e}")
            tracker = None

    if verbose:
        print("\n" + "=" * 80)
        print("UNIFIED ML PIPELINE - LET'S GO PREDICTIONDEX")
        print("=" * 80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Mode: {args.mode}")
        print(f"Dataset Version: {args.dataset_version}")
        print(f"Random Seed: {RANDOM_SEED}")
        print(f"Model Version: {args.version}")
        print(f"Scenario: {args.scenario_type}")
        if args.tune_hyperparams:
            print(f"GridSearch Type: {args.grid_type}")

    try:
        # Start MLflow run
        if tracker:
            run_name = f"{args.mode}_{args.dataset_version}_{args.version}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            tracker.start_run(run_name=run_name)

            # Log pipeline configuration
            tracker.log_params({
                'mode': args.mode,
                'dataset_version': args.dataset_version,
                'model_version': args.version,
                'scenario_type': args.scenario_type,
                'random_seed': RANDOM_SEED,
                'tune_hyperparams': args.tune_hyperparams,
                'model_type': args.model,
            })

        # STEP 1: Dataset preparation
        if args.mode in ['all', 'dataset']:
            success = run_dataset_preparation(
                dataset_version=args.dataset_version,
                scenario_type=args.scenario_type,
                num_random_samples=args.num_random_samples,
                max_combinations=args.max_combinations,
                verbose=verbose
            )
            if not success:
                sys.exit(1)

            if args.mode == 'dataset':
                print("\n✅ Dataset preparation complete!")
                return

        # Load datasets
        if verbose:
            print("\nLoading datasets...")

        train_path = PROCESSED_DIR / "train.parquet"
        test_path = PROCESSED_DIR / "test.parquet"

        if not train_path.exists() or not test_path.exists():
            print(f"\n❌ Datasets not found. Run with --mode=dataset first.")
            sys.exit(1)

        df_train = pd.read_parquet(train_path)
        df_test = pd.read_parquet(test_path)

        # Optional scenario filtering
        df_train, df_test = filter_by_scenario(df_train, df_test, args.scenario_type, verbose=verbose)

        # STEP 2: Feature engineering (using refactored class)
        feature_engineer = PokemonFeatureEngineer()
        X_train, X_test, y_train, y_test, scalers, feature_columns = feature_engineer.fit_transform(
            df_train, df_test, verbose=verbose
        )

        # Log dataset info to MLflow
        if tracker:
            tracker.log_dataset_info({
                "train_samples": len(X_train),
                "test_samples": len(X_test),
                "num_features": len(feature_columns)
            })

        # STEP 3 & 4: Train and evaluate (single model)
        if args.mode == 'train' or args.mode == 'evaluate':
            # Optional: Hyperparameter tuning
            if args.tune_hyperparams:
                model, best_params = tune_hyperparameters(X_train, y_train,
                                                          model_type=args.model,
                                                          verbose=verbose)
                hyperparams = best_params
            else:
                model = train_model(X_train, y_train, model_type=args.model, verbose=verbose)
                hyperparams = DEFAULT_XGBOOST_PARAMS if args.model == 'xgboost' else DEFAULT_RF_PARAMS

            # Evaluate
            metrics = evaluate_model(model, X_train, X_test, y_train, y_test,
                                     model_name=args.model, verbose=verbose)

            # Log to MLflow
            if tracker:
                tracker.log_params(hyperparams)
                tracker.log_metrics({
                    'train_accuracy': metrics['train_accuracy'],
                    'test_accuracy': metrics['test_accuracy'],
                    'test_precision': metrics['test_precision'],
                    'test_recall': metrics['test_recall'],
                    'test_f1': metrics['test_f1'],
                    'test_roc_auc': metrics['test_roc_auc'],
                    'overfitting': metrics['overfitting'],
                })

            # Feature importance
            analyze_feature_importance(model, feature_columns, verbose=verbose)

            # Export
            model_path = export_model(
                model,
                scalers,
                feature_columns,
                metrics,
                hyperparams=hyperparams,
                version=args.version,
                verbose=verbose)

            # Log model to MLflow
            if tracker and model_path:
                tracker.log_model(model, artifact_path=f"model_{args.version}",
                                  model_type=args.model, scalers=scalers,
                                  metadata={'feature_columns': feature_columns})

            if not args.skip_export_features:
                export_features(X_train, X_test, y_train, y_test, FEATURES_DIR, verbose=verbose)

        # STEP 5: Compare multiple models
        elif args.mode == 'compare':
            best_model, best_model_name, all_metrics = compare_models(
                X_train, X_test, y_train, y_test,
                models_to_compare=['xgboost', 'random_forest'],
                verbose=verbose
            )

            # Feature importance for best model
            analyze_feature_importance(best_model, feature_columns, verbose=verbose)

            # Export best model
            best_metrics = next(m for m in all_metrics if m['model_name'] == best_model_name)
            model_path = export_model(
                best_model,
                scalers,
                feature_columns,
                best_metrics,
                hyperparams=None,
                version=args.version,
                verbose=verbose)

            # Log to MLflow
            if tracker:
                for m in all_metrics:
                    tracker.log_metrics({
                        f"{m['model_name']}_test_accuracy": m['test_accuracy'],
                        f"{m['model_name']}_test_f1": m['test_f1'],
                    })
                if model_path:
                    tracker.log_model(best_model, artifact_path=f"model_{args.version}",
                                      model_type=best_model_name, scalers=scalers,
                                      metadata={'feature_columns': feature_columns})

                    # Register best model after comparison
                    model_name = "battle_winner_predictor"
                    best_metric = next(m for m in all_metrics if m['model_name'] == best_model_name)
                    description = f"{best_model_name} (winner after comparison) - Accuracy: {best_metric['test_accuracy']:.4f}"
                    version_number = tracker.register_model(model_name=model_name, description=description)

                    if version_number and best_metric.get('test_accuracy', 0) >= 0.85:
                        if verbose:
                            print(f"\n🎯 Best model meets quality threshold")
                        tracker.promote_to_production(model_name, version_number)

            if not args.skip_export_features:
                export_features(X_train, X_test, y_train, y_test, FEATURES_DIR, verbose=verbose)

        # STEP 6: Complete pipeline
        elif args.mode == 'all':
            # Compare models
            best_model, best_model_name, all_metrics = compare_models(
                X_train, X_test, y_train, y_test,
                models_to_compare=['xgboost', 'random_forest'],
                verbose=verbose
            )

            # Optional: Hyperparameter tuning on best model
            if args.tune_hyperparams and best_model_name == 'xgboost':
                if verbose:
                    print("\n🔧 Running hyperparameter tuning on best model...")
                best_model, best_params = tune_hyperparameters(X_train, y_train,
                                                               model_type='xgboost',
                                                               verbose=verbose)
                # Re-evaluate
                metrics = evaluate_model(best_model, X_train, X_test, y_train, y_test,
                                         model_name='xgboost_tuned', verbose=verbose)
                hyperparams = best_params
            else:
                metrics = next(m for m in all_metrics if m['model_name'] == best_model_name)
                hyperparams = None

            # Feature importance
            analyze_feature_importance(best_model, feature_columns, verbose=verbose)

            # Export
            model_path = export_model(
                best_model,
                scalers,
                feature_columns,
                metrics,
                hyperparams=hyperparams,
                version=args.version,
                verbose=verbose)

            # Log to MLflow
            if tracker:
                if hyperparams:
                    tracker.log_params(hyperparams)
                tracker.log_metrics({
                    'train_accuracy': metrics['train_accuracy'],
                    'test_accuracy': metrics['test_accuracy'],
                    'test_precision': metrics['test_precision'],
                    'test_recall': metrics['test_recall'],
                    'test_f1': metrics['test_f1'],
                    'test_roc_auc': metrics['test_roc_auc'],
                    'overfitting': metrics['overfitting'],
                })
                if model_path:
                    tracker.log_model(best_model, artifact_path=f"model_{args.version}",
                                      model_type=best_model_name, scalers=scalers,
                                      metadata={'feature_columns': feature_columns})

                    # Register model in MLflow Model Registry
                    model_name = "battle_winner_predictor"
                    description = f"{best_model_name} - Accuracy: {metrics['test_accuracy']:.4f}, ROC-AUC: {metrics['test_roc_auc']:.4f}"
                    version_number = tracker.register_model(model_name=model_name, description=description)

                    # Auto-promote to Production if metrics are good
                    if version_number and metrics.get('test_accuracy', 0) >= 0.85:
                        if verbose:
                            print(f"\n🎯 Model meets quality threshold (accuracy >= 0.85)")
                        tracker.promote_to_production(model_name, version_number)
                    elif version_number:
                        if verbose:
                            print(f"\n⚠️  Model registered but not promoted (accuracy < 0.85)")
                            print(f"   Manual promotion: mlflow models transition-to-staging/production")

            if not args.skip_export_features:
                export_features(X_train, X_test, y_train, y_test, FEATURES_DIR, verbose=verbose)

        # Final summary
        if verbose:
            print("\n" + "=" * 80)
            print("🎉 PIPELINE COMPLETE!")
            print("=" * 80)
            if args.mode in ['train', 'evaluate', 'compare', 'all']:
                print(f"\n✅ Model trained and exported successfully")
                print(f"✅ Test Accuracy: {metrics.get('test_accuracy', 0)*100:.2f}%")
                print(f"✅ Test ROC-AUC: {metrics.get('test_roc_auc', 0):.4f}")
                print(f"\n📁 Model artifacts: {MODELS_DIR}")
                if not args.skip_export_features:
                    print(f"📁 Features: {FEATURES_DIR}")

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
