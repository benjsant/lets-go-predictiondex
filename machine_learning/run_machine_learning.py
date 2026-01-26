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

import os
import sys
import argparse
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
import pickle
import joblib  # For RandomForest model compression

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    classification_report, confusion_matrix, roc_curve
)
from sklearn.model_selection import cross_val_score, GridSearchCV
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier

# MLflow integration (C13 - MLOps)
try:
    from machine_learning.mlflow_integration import get_mlflow_tracker
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    print("⚠️  MLflow not available - tracking disabled")

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Paths (will be set based on --dataset-version)
DATA_DIR_V1 = PROJECT_ROOT / "data" / "ml" / "battle_winner"
DATA_DIR_V2 = PROJECT_ROOT / "data" / "ml" / "battle_winner_v2"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports" / "ml"

# Global paths (set by main based on args)
DATA_DIR = None
RAW_DIR = None
PROCESSED_DIR = None
FEATURES_DIR = None

# Random seed
RANDOM_SEED = 42

# Default hyperparameters (optimized for CPU)
DEFAULT_XGBOOST_PARAMS = {
    'n_estimators': 100,
    'max_depth': 8,
    'learning_rate': 0.1,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'tree_method': 'hist',        # CPU-optimized histogram algorithm (faster than 'auto')
    'predictor': 'cpu_predictor', # Explicit CPU predictor
    'random_state': RANDOM_SEED,
    'n_jobs': -1,                 # Use all CPU cores
    'eval_metric': 'logloss',
}

DEFAULT_RF_PARAMS = {
    'n_estimators': 50,  # Reduced from 100 (less trees = smaller model)
    'max_depth': 12,     # Reduced from 15 (shallower trees = smaller model)
    'min_samples_split': 10,  # Increased from 5 (prevents overfitting + smaller)
    'min_samples_leaf': 4,    # Increased from 2 (fewer leaf nodes)
    'random_state': RANDOM_SEED,
    'n_jobs': -1,
}

# Hyperparameter search space (optimized grid for CPU performance)
# Reduced combinations but maintains quality: 2×3×2×1×1 = 12 combinations (vs 243 before)
XGBOOST_PARAM_GRID = {
    'n_estimators': [100, 200],           # 2 values: baseline + double
    'max_depth': [6, 8, 10],              # 3 values: shallow, medium, deep
    'learning_rate': [0.05, 0.1],         # 2 values: conservative + standard
    'subsample': [0.8],                   # 1 value: optimal known value
    'colsample_bytree': [0.8],            # 1 value: optimal known value
    'tree_method': ['hist'],              # CPU-optimized method
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

def engineer_features(df_train: pd.DataFrame, df_test: pd.DataFrame, verbose: bool = True) -> Tuple:
    """
    Feature engineering pipeline matching train_model.py exactly.

    Steps:
    1. One-hot encode categorical features (types)
    2. Remove original categorical columns and IDs
    3. Normalize numerical features with StandardScaler
    4. Create 6 derived features using original values
    5. Normalize derived features with a second StandardScaler

    Validation: C12 (preprocessing pipeline tests)

    Returns:
        X_train, X_test, y_train, y_test, scalers_dict, feature_columns
    """
    if verbose:
        print("\n" + "=" * 80)
        print("STEP 2: FEATURE ENGINEERING")
        print("=" * 80)

    # Separate target
    y_train = df_train['winner']
    y_test = df_test['winner']

    X_train_encoded = df_train.drop(columns=['winner']).copy()
    X_test_encoded = df_test.drop(columns=['winner']).copy()

    # One-hot encoding
    if verbose:
        print("\n1️⃣ One-hot encoding categorical features...")

    categorical_features = ['a_type_1', 'a_type_2', 'b_type_1', 'b_type_2', 'a_move_type', 'b_move_type']

    for feature in categorical_features:
        if feature in X_train_encoded.columns:
            train_dummies = pd.get_dummies(X_train_encoded[feature], prefix=feature, drop_first=False)
            test_dummies = pd.get_dummies(X_test_encoded[feature], prefix=feature, drop_first=False)

            # Align columns
            train_dummies, test_dummies = train_dummies.align(test_dummies, join='left', axis=1, fill_value=0)

            X_train_encoded = pd.concat([X_train_encoded, train_dummies], axis=1)
            X_test_encoded = pd.concat([X_test_encoded, test_dummies], axis=1)

    if verbose:
        print(f"   After encoding: {X_train_encoded.shape[1]} columns")

    # Remove categorical columns and IDs
    id_features = ['pokemon_a_id', 'pokemon_b_id', 'pokemon_a_name', 'pokemon_b_name', 'a_move_name', 'b_move_name']
    columns_to_drop = categorical_features + id_features
    if 'scenario_type' in X_train_encoded.columns:
        columns_to_drop.append('scenario_type')
    columns_to_drop = [col for col in columns_to_drop if col in X_train_encoded.columns]

    X_train_encoded.drop(columns=columns_to_drop, inplace=True)
    X_test_encoded.drop(columns=columns_to_drop, inplace=True)

    if verbose:
        print(f"   After dropping categorical/IDs: {X_train_encoded.shape[1]} columns")

    # Normalize numerical features
    if verbose:
        print("\n2️⃣ Normalizing numerical features...")

    features_to_scale = [
        'a_hp', 'a_attack', 'a_defense', 'a_sp_attack', 'a_sp_defense', 'a_speed',
        'b_hp', 'b_attack', 'b_defense', 'b_sp_attack', 'b_sp_defense', 'b_speed',
        'a_move_power', 'b_move_power',
        'a_total_stats', 'b_total_stats',
        'speed_diff', 'hp_diff'
    ]
    features_to_scale = [f for f in features_to_scale if f in X_train_encoded.columns]

    scaler = StandardScaler()
    X_train_encoded[features_to_scale] = scaler.fit_transform(X_train_encoded[features_to_scale])
    X_test_encoded[features_to_scale] = scaler.transform(X_test_encoded[features_to_scale])

    if verbose:
        print(f"   {len(features_to_scale)} features normalized")

    # Create derived features
    if verbose:
        print("\n3️⃣ Creating derived features...")

    X_train_encoded['stat_ratio'] = df_train['a_total_stats'] / (df_train['b_total_stats'] + 1)
    X_test_encoded['stat_ratio'] = df_test['a_total_stats'] / (df_test['b_total_stats'] + 1)

    X_train_encoded['type_advantage_diff'] = df_train['a_move_type_mult'] - df_train['b_move_type_mult']
    X_test_encoded['type_advantage_diff'] = df_test['a_move_type_mult'] - df_test['b_move_type_mult']

    X_train_encoded['effective_power_a'] = (
        df_train['a_move_power'] * df_train['a_move_stab'] * df_train['a_move_type_mult']
    )
    X_test_encoded['effective_power_a'] = (
        df_test['a_move_power'] * df_test['a_move_stab'] * df_test['a_move_type_mult']
    )

    X_train_encoded['effective_power_b'] = (
        df_train['b_move_power'] * df_train['b_move_stab'] * df_train['b_move_type_mult']
    )
    X_test_encoded['effective_power_b'] = (
        df_test['b_move_power'] * df_test['b_move_stab'] * df_test['b_move_type_mult']
    )

    X_train_encoded['effective_power_diff'] = (
        X_train_encoded['effective_power_a'] - X_train_encoded['effective_power_b']
    )
    X_test_encoded['effective_power_diff'] = (
        X_test_encoded['effective_power_a'] - X_test_encoded['effective_power_b']
    )

    X_train_encoded['priority_advantage'] = df_train['a_move_priority'] - df_train['b_move_priority']
    X_test_encoded['priority_advantage'] = df_test['a_move_priority'] - df_test['b_move_priority']

    if verbose:
        print(f"   After derived features: {X_train_encoded.shape[1]} columns")

    # Normalize derived features
    if verbose:
        print("\n4️⃣ Normalizing derived features...")

    new_features = [
        'stat_ratio', 'type_advantage_diff',
        'effective_power_a', 'effective_power_b',
        'effective_power_diff', 'priority_advantage'
    ]

    scaler_new = StandardScaler()
    X_train_encoded[new_features] = scaler_new.fit_transform(X_train_encoded[new_features])
    X_test_encoded[new_features] = scaler_new.transform(X_test_encoded[new_features])

    if verbose:
        print(f"   {len(new_features)} derived features normalized")
        print(f"\n✅ Final feature count: {X_train_encoded.shape[1]}")

    scalers = {
        'standard_scaler': scaler,
        'standard_scaler_new_features': scaler_new
    }

    return X_train_encoded, X_test_encoded, y_train, y_test, scalers, X_train_encoded.columns.tolist()


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
        base_model = xgb.XGBClassifier(random_state=RANDOM_SEED, n_jobs=-1)
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
        n_jobs=-1,              # Parallelize CV folds across all cores
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

def evaluate_model(model: Any, X_train: pd.DataFrame, X_test: pd.DataFrame,
                   y_train: pd.Series, y_test: pd.Series,
                   model_name: str = "Model",
                   verbose: bool = True) -> Dict[str, float]:
    """
    Comprehensive model evaluation.

    Validation: C12 (evaluation tests)

    Returns:
        Dictionary of metrics
    """
    if verbose:
        print("\n" + "=" * 80)
        print(f"STEP 4: MODEL EVALUATION - {model_name}")
        print("=" * 80)

    # Predictions
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)

    # Probabilities for ROC-AUC
    y_train_proba = model.predict_proba(X_train)[:, 1]
    y_test_proba = model.predict_proba(X_test)[:, 1]

    # Calculate metrics
    metrics = {
        'model_name': model_name,
        'train_accuracy': accuracy_score(y_train, y_train_pred),
        'test_accuracy': accuracy_score(y_test, y_test_pred),
        'test_precision': precision_score(y_test, y_test_pred),
        'test_recall': recall_score(y_test, y_test_pred),
        'test_f1': f1_score(y_test, y_test_pred),
        'test_roc_auc': roc_auc_score(y_test, y_test_proba),
        'train_samples': len(y_train),
        'test_samples': len(y_test),
    }

    # Overfitting check
    overfitting = metrics['train_accuracy'] - metrics['test_accuracy']
    metrics['overfitting'] = overfitting

    if verbose:
        print("\n📊 PERFORMANCE METRICS")
        print("-" * 80)
        print(f"Train Accuracy:  {metrics['train_accuracy']:.4f}")
        print(f"Test Accuracy:   {metrics['test_accuracy']:.4f}")
        print(f"Test Precision:  {metrics['test_precision']:.4f}")
        print(f"Test Recall:     {metrics['test_recall']:.4f}")
        print(f"Test F1-Score:   {metrics['test_f1']:.4f}")
        print(f"Test ROC-AUC:    {metrics['test_roc_auc']:.4f}")
        print(f"\nOverfitting:     {overfitting:.4f} ({overfitting*100:.2f}%)")

        # Classification report
        print("\n" + "-" * 80)
        print("CLASSIFICATION REPORT (Test Set)")
        print("-" * 80)
        print(classification_report(y_test, y_test_pred, target_names=['B wins', 'A wins']))

        # Confusion matrix
        print("Confusion Matrix:")
        cm = confusion_matrix(y_test, y_test_pred)
        print(cm)
        print(f"\nTrue Negatives:  {cm[0, 0]}")
        print(f"False Positives: {cm[0, 1]}")
        print(f"False Negatives: {cm[1, 0]}")
        print(f"True Positives:  {cm[1, 1]}")

    return metrics


def analyze_feature_importance(model: Any, feature_columns: List[str],
                                top_n: int = 20,
                                verbose: bool = True) -> pd.DataFrame:
    """
    Analyze and display feature importance.

    Validation: C12 (feature analysis tests)

    Returns:
        DataFrame with feature importances
    """
    if verbose:
        print("\n" + "=" * 80)
        print("FEATURE IMPORTANCE ANALYSIS")
        print("=" * 80)

    # Get feature importances
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
    else:
        if verbose:
            print("\n⚠️  Model does not support feature_importances_")
        return pd.DataFrame()

    # Create DataFrame
    importance_df = pd.DataFrame({
        'feature': feature_columns,
        'importance': importances
    }).sort_values('importance', ascending=False)

    if verbose:
        print(f"\nTop {top_n} Most Important Features:")
        print("-" * 80)
        for i, row in importance_df.head(top_n).iterrows():
            print(f"{row['feature']:40s} {row['importance']:.6f}")

    return importance_df


# ================================================================
# STEP 5: MODEL COMPARISON
# ================================================================

def compare_models(X_train: pd.DataFrame, X_test: pd.DataFrame,
                   y_train: pd.Series, y_test: pd.Series,
                   models_to_compare: List[str] = ['xgboost', 'random_forest'],
                   verbose: bool = True) -> Tuple[Any, str, Dict]:
    """
    Train and compare multiple models.

    Validation: C12 (model comparison tests)

    Returns:
        best_model, best_model_name, all_metrics
    """
    if verbose:
        print("\n" + "=" * 80)
        print("STEP 5: MODEL COMPARISON")
        print("=" * 80)
        print(f"\nComparing models: {', '.join(models_to_compare)}")

    results = []
    trained_models = {}

    for model_type in models_to_compare:
        if verbose:
            print(f"\n{'─' * 80}")
            print(f"Training {model_type}...")

        # Train model
        model = train_model(X_train, y_train, model_type=model_type, verbose=False)
        trained_models[model_type] = model

        # Evaluate model
        metrics = evaluate_model(model, X_train, X_test, y_train, y_test,
                                model_name=model_type, verbose=False)
        results.append(metrics)

        if verbose:
            print(f"✅ {model_type}: Test Accuracy = {metrics['test_accuracy']:.4f}")

    # Create comparison DataFrame
    results_df = pd.DataFrame(results)

    if verbose:
        print("\n" + "=" * 80)
        print("COMPARISON RESULTS")
        print("=" * 80)
        print("\n", results_df[['model_name', 'test_accuracy', 'test_f1', 'test_roc_auc', 'overfitting']].to_string(index=False))

    # Select best model
    best_idx = results_df['test_accuracy'].idxmax()
    best_model_name = results_df.loc[best_idx, 'model_name']
    best_model = trained_models[best_model_name]

    if verbose:
        print(f"\n🏆 BEST MODEL: {best_model_name}")
        print(f"   Test Accuracy: {results_df.loc[best_idx, 'test_accuracy']:.4f}")
        print(f"   Test ROC-AUC:  {results_df.loc[best_idx, 'test_roc_auc']:.4f}")

    return best_model, best_model_name, results_df.to_dict('records')


# ================================================================
# STEP 6: MODEL EXPORT
# ================================================================

def export_model(model: Any, scalers: Dict, feature_columns: List[str],
                 metrics: Dict, hyperparams: Optional[Dict] = None,
                 version: str = "v1", verbose: bool = True):
    """
    Export trained model, scalers, and metadata.

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
    with open(metadata_json_path, 'w') as f:
        json.dump(metadata_json, f, indent=2)
    if verbose:
        print(f"✅ Metadata (JSON) exported: {metadata_json_path}")
        print(f"\n✅ All artifacts exported to: {MODELS_DIR}")

    return str(model_path)  # Return path for MLflow logging


def export_features(X_train: pd.DataFrame, X_test: pd.DataFrame,
                    y_train: pd.Series, y_test: pd.Series,
                    verbose: bool = True):
    """Export feature-engineered datasets for reproducibility."""
    if verbose:
        print("\nExporting feature-engineered datasets...")

    FEATURES_DIR.mkdir(parents=True, exist_ok=True)

    X_train.to_parquet(FEATURES_DIR / "X_train.parquet", index=False, engine='pyarrow')
    X_test.to_parquet(FEATURES_DIR / "X_test.parquet", index=False, engine='pyarrow')
    y_train.to_frame('winner').to_parquet(FEATURES_DIR / "y_train.parquet", index=False, engine='pyarrow')
    y_test.to_frame('winner').to_parquet(FEATURES_DIR / "y_test.parquet", index=False, engine='pyarrow')

    if verbose:
        print(f"✅ Features exported to: {FEATURES_DIR}")


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
    
    # Set global paths based on dataset version
    global DATA_DIR, RAW_DIR, PROCESSED_DIR, FEATURES_DIR
    DATA_DIR = DATA_DIR_V2 if args.dataset_version == 'v2' else DATA_DIR_V1
    RAW_DIR = DATA_DIR / "raw"
    PROCESSED_DIR = DATA_DIR / "processed"
    FEATURES_DIR = DATA_DIR / "features"

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

        # STEP 2: Feature engineering
        X_train, X_test, y_train, y_test, scalers, feature_columns = engineer_features(
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
            model_path = export_model(model, scalers, feature_columns, metrics, hyperparams, version=args.version, verbose=verbose)
            
            # Log model to MLflow
            if tracker and model_path:
                tracker.log_model(model, artifact_path=f"model_{args.version}", 
                                model_type=args.model, scalers=scalers, 
                                metadata={'feature_columns': feature_columns})

            if not args.skip_export_features:
                export_features(X_train, X_test, y_train, y_test, verbose=verbose)

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
            model_path = export_model(best_model, scalers, feature_columns, best_metrics, hyperparams=None, version=args.version, verbose=verbose)

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
                export_features(X_train, X_test, y_train, y_test, verbose=verbose)

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
            model_path = export_model(best_model, scalers, feature_columns, metrics, hyperparams, version=args.version, verbose=verbose)

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
                export_features(X_train, X_test, y_train, y_test, verbose=verbose)

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
