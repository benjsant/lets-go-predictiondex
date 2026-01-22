#!/usr/bin/env python3
"""
Unified ML Pipeline - Let's Go PredictionDex (V2)
=================================================

- Fix: proper try/except in scenario filtering
- Improved robustness
- Compatible with original 956-line pipeline
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

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Paths
DATA_DIR = PROJECT_ROOT / "data" / "ml" / "battle_winner"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
FEATURES_DIR = DATA_DIR / "features"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports" / "ml"

# Random seed
RANDOM_SEED = 42

# Default hyperparameters
DEFAULT_XGBOOST_PARAMS = {
    'n_estimators': 100,
    'max_depth': 8,
    'learning_rate': 0.1,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'random_state': RANDOM_SEED,
    'n_jobs': -1,
    'eval_metric': 'logloss',
}

DEFAULT_RF_PARAMS = {
    'n_estimators': 100,
    'max_depth': 15,
    'min_samples_split': 5,
    'min_samples_leaf': 2,
    'random_state': RANDOM_SEED,
    'n_jobs': -1,
}

# Hyperparameter search space
XGBOOST_PARAM_GRID = {
    'n_estimators': [50, 100, 200],
    'max_depth': [6, 8, 10],
    'learning_rate': [0.05, 0.1, 0.2],
    'subsample': [0.7, 0.8, 0.9],
    'colsample_bytree': [0.7, 0.8, 0.9],
}

# ================================================================
# STEP 1: DATASET PREPARATION
# ================================================================

def run_dataset_preparation(verbose: bool = True) -> bool:
    """Run dataset preparation script to generate train/test datasets."""
    if verbose:
        print("\n" + "=" * 80)
        print("STEP 1: DATASET PREPARATION")
        print("=" * 80)
        print("\nGenerating Pokemon battle datasets from database...")

    try:
        # Run build_battle_winner_dataset.py
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "machine_learning" / "build_battle_winner_dataset.py")],
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

        # Load datasets for basic validation
        df_train = pd.read_parquet(train_path)
        df_test = pd.read_parquet(test_path)

        if verbose:
            print("\n✅ Dataset validation:")
            print(f"   Train samples: {len(df_train):,}")
            print(f"   Test samples: {len(df_test):,}")
            print(f"   Total features: {df_train.shape[1]}")

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

    Fix V2: properly enclosed in try/except, return full dataset on error
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

        # If filtering leads to empty dataset, fallback
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

    Returns:
        X_train, X_test, y_train, y_test, scalers_dict, feature_columns
    """
    if verbose:
        print("\n" + "=" * 80)
        print("STEP 2: FEATURE ENGINEERING")
        print("=" * 80)

    y_train = df_train['winner']
    y_test = df_test['winner']

    X_train_encoded = df_train.drop(columns=['winner']).copy()
    X_test_encoded = df_test.drop(columns=['winner']).copy()

    # One-hot encoding categorical features
    categorical_features = ['a_type_1', 'a_type_2', 'b_type_1', 'b_type_2', 'a_move_type', 'b_move_type']
    for feature in categorical_features:
        if feature in X_train_encoded.columns:
            train_dummies = pd.get_dummies(X_train_encoded[feature], prefix=feature, drop_first=False)
            test_dummies = pd.get_dummies(X_test_encoded[feature], prefix=feature, drop_first=False)
            train_dummies, test_dummies = train_dummies.align(test_dummies, join='left', axis=1, fill_value=0)
            X_train_encoded = pd.concat([X_train_encoded, train_dummies], axis=1)
            X_test_encoded = pd.concat([X_test_encoded, test_dummies], axis=1)

    # Remove categorical and ID columns
    id_features = ['pokemon_a_id', 'pokemon_b_id', 'pokemon_a_name', 'pokemon_b_name', 'a_move_name', 'b_move_name']
    columns_to_drop = [col for col in categorical_features + id_features if col in X_train_encoded.columns]
    if 'scenario_type' in X_train_encoded.columns:
        columns_to_drop.append('scenario_type')
    X_train_encoded.drop(columns=columns_to_drop, inplace=True)
    X_test_encoded.drop(columns=columns_to_drop, inplace=True)

    # Normalize numeric features
    features_to_scale = [
        'a_hp', 'a_attack', 'a_defense', 'a_sp_attack', 'a_sp_defense', 'a_speed',
        'b_hp', 'b_attack', 'b_defense', 'b_sp_attack', 'b_sp_defense', 'b_speed',
        'a_move_power', 'b_move_power', 'a_total_stats', 'b_total_stats', 'speed_diff', 'hp_diff'
    ]
    features_to_scale = [f for f in features_to_scale if f in X_train_encoded.columns]
    scaler = StandardScaler()
    X_train_encoded[features_to_scale] = scaler.fit_transform(X_train_encoded[features_to_scale])
    X_test_encoded[features_to_scale] = scaler.transform(X_test_encoded[features_to_scale])

    # Derived features
    X_train_encoded['stat_ratio'] = df_train['a_total_stats'] / (df_train['b_total_stats'] + 1)
    X_test_encoded['stat_ratio'] = df_test['a_total_stats'] / (df_test['b_total_stats'] + 1)
    X_train_encoded['type_advantage_diff'] = df_train['a_move_type_mult'] - df_train['b_move_type_mult']
    X_test_encoded['type_advantage_diff'] = df_test['a_move_type_mult'] - df_test['b_move_type_mult']
    X_train_encoded['effective_power_a'] = df_train['a_move_power'] * df_train['a_move_stab'] * df_train['a_move_type_mult']
    X_test_encoded['effective_power_a'] = df_test['a_move_power'] * df_test['a_move_stab'] * df_test['a_move_type_mult']
    X_train_encoded['effective_power_b'] = df_train['b_move_power'] * df_train['b_move_stab'] * df_train['b_move_type_mult']
    X_test_encoded['effective_power_b'] = df_test['b_move_power'] * df_test['b_move_stab'] * df_test['b_move_type_mult']
    X_train_encoded['effective_power_diff'] = X_train_encoded['effective_power_a'] - X_train_encoded['effective_power_b']
    X_test_encoded['effective_power_diff'] = X_test_encoded['effective_power_a'] - X_test_encoded['effective_power_b']
    X_train_encoded['priority_advantage'] = df_train['a_move_priority'] - df_train['b_move_priority']
    X_test_encoded['priority_advantage'] = df_test['a_move_priority'] - df_test['b_move_priority']

    # Normalize derived features
    new_features = ['stat_ratio', 'type_advantage_diff', 'effective_power_a', 'effective_power_b', 'effective_power_diff', 'priority_advantage']
    scaler_new = StandardScaler()
    X_train_encoded[new_features] = scaler_new.fit_transform(X_train_encoded[new_features])
    X_test_encoded[new_features] = scaler_new.transform(X_test_encoded[new_features])

    scalers = {'standard_scaler': scaler, 'standard_scaler_new_features': scaler_new}

    return X_train_encoded, X_test_encoded, y_train, y_test, scalers, X_train_encoded.columns.tolist()
