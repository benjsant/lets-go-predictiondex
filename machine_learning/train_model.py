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

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR_V1 = PROJECT_ROOT / "data" / "ml" / "battle_winner"
DATA_DIR_V2 = PROJECT_ROOT / "data" / "ml" / "battle_winner_v2"
MODELS_DIR = PROJECT_ROOT / "models"

# Will be set based on --dataset-version argument
DATA_DIR = None
PROCESSED_DIR = None
FEATURES_DIR = None

# Random seed for reproducibility
RANDOM_SEED = 42

# XGBoost hyperparameters (optimized for CPU)
XGBOOST_PARAMS = {
    'n_estimators': 100,
    'max_depth': 8,
    'learning_rate': 0.1,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'tree_method': 'hist',        # CPU-optimized histogram algorithm
    'predictor': 'cpu_predictor',  # Explicit CPU predictor
    'random_state': RANDOM_SEED,
    'n_jobs': -1,                 # Use all CPU cores
    'eval_metric': 'logloss',
}

# GridSearchCV parameter grids (CPU-optimized)
# Conservative grid for fast training (CI/docker)
# 2×2×2×1×1 = 8 combinations (~5-10 min)
XGBOOST_PARAM_GRID_FAST = {
    'n_estimators': [100, 150],
    'max_depth': [6, 8],
    'learning_rate': [0.05, 0.1],
    'subsample': [0.8],
    'colsample_bytree': [0.8],
    'tree_method': ['hist'],  # CPU-optimized
}

# Extended grid for notebooks (better accuracy)
# 3×3×2×1×1 = 18 combinations (~15-30 min)
XGBOOST_PARAM_GRID_EXTENDED = {
    'n_estimators': [100, 150, 200],
    'max_depth': [6, 8, 10],
    'learning_rate': [0.05, 0.1],      # Reduced from 3 to 2 values
    'subsample': [0.8],                # Fixed to optimal
    'colsample_bytree': [0.8],         # Fixed to optimal
    'tree_method': ['hist'],           # CPU-optimized
}

# Default grid
XGBOOST_PARAM_GRID = XGBOOST_PARAM_GRID_FAST


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


def engineer_features(df_train, df_test):
    """
    Feature engineering pipeline matching notebook 02 exactly.

    Steps (matching notebook 02):
    1. Separate features and target
    2. One-hot encode categorical features (types) - creates ~102 columns
    3. Remove original categorical columns and IDs
    4. Normalize numerical features with StandardScaler
    5. Create 6 derived features using original values
    6. Normalize derived features with a second StandardScaler

    Returns:
        X_train, X_test, y_train, y_test, scalers_dict, feature_columns
    """
    print("\nFeature engineering...")

    # === Step 1: Separate target ===
    y_train = df_train['winner']
    y_test = df_test['winner']

    # === Step 2: Copy datasets ===
    X_train_encoded = df_train.drop(columns=['winner']).copy()
    X_test_encoded = df_test.drop(columns=['winner']).copy()

    # === Step 3: One-hot encoding ===
    print("  1️⃣ One-hot encoding categorical features...")

    categorical_features = ['a_type_1', 'a_type_2', 'b_type_1', 'b_type_2', 'a_move_type', 'b_move_type']

    for feature in categorical_features:
        if feature in X_train_encoded.columns:
            # One-hot encode
            train_dummies = pd.get_dummies(X_train_encoded[feature], prefix=feature, drop_first=False)
            test_dummies = pd.get_dummies(X_test_encoded[feature], prefix=feature, drop_first=False)

            # Align columns
            train_dummies, test_dummies = train_dummies.align(test_dummies, join='left', axis=1, fill_value=0)

            # Add to dataset
            X_train_encoded = pd.concat([X_train_encoded, train_dummies], axis=1)
            X_test_encoded = pd.concat([X_test_encoded, test_dummies], axis=1)

    print(f"     After encoding: {X_train_encoded.shape[1]} columns")

    # === Step 4: Remove categorical columns and IDs ===
    id_features = ['pokemon_a_id', 'pokemon_b_id', 'pokemon_a_name', 'pokemon_b_name', 'a_move_name', 'b_move_name']

    # Add scenario_type to columns to drop if present (not used as feature)
    if 'scenario_type' in X_train_encoded.columns:
        id_features.append('scenario_type')
        print("  ℹ️  Removing 'scenario_type' column (metadata, not a feature)")

    columns_to_drop = categorical_features + id_features
    if 'scenario_type' in X_train_encoded.columns:
        columns_to_drop.append('scenario_type')
    columns_to_drop = [col for col in columns_to_drop if col in X_train_encoded.columns]

    X_train_encoded.drop(columns=columns_to_drop, inplace=True)
    X_test_encoded.drop(columns=columns_to_drop, inplace=True)

    print(f"     After dropping categorical/IDs: {X_train_encoded.shape[1]} columns")

    # === Step 5: Normalize numerical features ===
    print("  2️⃣ Normalizing numerical features...")

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

    print(f"     {len(features_to_scale)} features normalized")

    # === Step 6: Create derived features (using original values from df_train/df_test) ===
    print("  3️⃣ Creating derived features...")

    # 1. stat_ratio
    X_train_encoded['stat_ratio'] = df_train['a_total_stats'] / (df_train['b_total_stats'] + 1)
    X_test_encoded['stat_ratio'] = df_test['a_total_stats'] / (df_test['b_total_stats'] + 1)

    # 2. type_advantage_diff
    X_train_encoded['type_advantage_diff'] = df_train['a_move_type_mult'] - df_train['b_move_type_mult']
    X_test_encoded['type_advantage_diff'] = df_test['a_move_type_mult'] - df_test['b_move_type_mult']

    # 3. effective_power_a
    X_train_encoded['effective_power_a'] = (
        df_train['a_move_power'] * df_train['a_move_stab'] * df_train['a_move_type_mult']
    )
    X_test_encoded['effective_power_a'] = (
        df_test['a_move_power'] * df_test['a_move_stab'] * df_test['a_move_type_mult']
    )

    # 4. effective_power_b
    X_train_encoded['effective_power_b'] = (
        df_train['b_move_power'] * df_train['b_move_stab'] * df_train['b_move_type_mult']
    )
    X_test_encoded['effective_power_b'] = (
        df_test['b_move_power'] * df_test['b_move_stab'] * df_test['b_move_type_mult']
    )

    # 5. effective_power_diff
    X_train_encoded['effective_power_diff'] = (
        X_train_encoded['effective_power_a'] - X_train_encoded['effective_power_b']
    )
    X_test_encoded['effective_power_diff'] = (
        X_test_encoded['effective_power_a'] - X_test_encoded['effective_power_b']
    )

    # 6. priority_advantage
    X_train_encoded['priority_advantage'] = df_train['a_move_priority'] - df_train['b_move_priority']
    X_test_encoded['priority_advantage'] = df_test['a_move_priority'] - df_test['b_move_priority']

    print(f"     After derived features: {X_train_encoded.shape[1]} columns")

    # === Step 7: Normalize new derived features ===
    print("  4️⃣ Normalizing derived features...")

    new_features = [
        'stat_ratio', 'type_advantage_diff',
        'effective_power_a', 'effective_power_b',
        'effective_power_diff', 'priority_advantage'
    ]

    scaler_new = StandardScaler()
    X_train_encoded[new_features] = scaler_new.fit_transform(X_train_encoded[new_features])
    X_test_encoded[new_features] = scaler_new.transform(X_test_encoded[new_features])

    print(f"     {len(new_features)} derived features normalized")

    print(f"\n  ✅ Final feature count: {X_train_encoded.shape[1]}")

    # Package scalers
    scalers = {
        'standard_scaler': scaler,
        'standard_scaler_new_features': scaler_new
    }

    return X_train_encoded, X_test_encoded, y_train, y_test, scalers, X_train_encoded.columns.tolist()


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


def evaluate_model(model, X_train, X_test, y_train, y_test):
    """Evaluate model performance on train and test sets."""
    print("\nEvaluating model...")

    # Predictions
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)

    # Probabilities for ROC-AUC
    y_train_proba = model.predict_proba(X_train)[:, 1]
    y_test_proba = model.predict_proba(X_test)[:, 1]

    # Metrics
    metrics = {
        'train_accuracy': accuracy_score(y_train, y_train_pred),
        'test_accuracy': accuracy_score(y_test, y_test_pred),
        'test_precision': precision_score(y_test, y_test_pred),
        'test_recall': recall_score(y_test, y_test_pred),
        'test_f1': f1_score(y_test, y_test_pred),
        'test_roc_auc': roc_auc_score(y_test, y_test_proba),
    }

    # Print results
    print("\n" + "=" * 60)
    print("MODEL PERFORMANCE")
    print("=" * 60)
    print(f"Train Accuracy: {metrics['train_accuracy']:.4f}")
    print(f"Test Accuracy:  {metrics['test_accuracy']:.4f}")
    print(f"Test Precision: {metrics['test_precision']:.4f}")
    print(f"Test Recall:    {metrics['test_recall']:.4f}")
    print(f"Test F1-Score:  {metrics['test_f1']:.4f}")
    print(f"Test ROC-AUC:   {metrics['test_roc_auc']:.4f}")

    # Overfitting check
    overfitting = metrics['train_accuracy'] - metrics['test_accuracy']
    print(f"\nOverfitting: {overfitting:.4f} ({overfitting*100:.2f}%)")

    # Classification report
    print("\n" + "=" * 60)
    print("CLASSIFICATION REPORT (Test Set)")
    print("=" * 60)
    print(classification_report(y_test, y_test_pred, target_names=['B wins', 'A wins']))

    # Confusion matrix
    print("Confusion Matrix:")
    cm = confusion_matrix(y_test, y_test_pred)
    print(cm)

    return metrics


def export_model(model, scalers, feature_columns, metrics, version: str, best_params: dict, grid_used: bool):
    """Export trained model, scalers, and metadata with optimal compression."""
    print("\nExporting model artifacts...")

    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # Export model with compression based on model type
    model_path = MODELS_DIR / f"battle_winner_model_{version}.pkl"
    model_type = type(model).__name__

    if model_type == 'RandomForestClassifier':
        # Use joblib with aggressive compression for RandomForest (5-10x smaller)
        joblib.dump(model, model_path, compress=('zlib', 9))
        print(f"  Model (joblib compressed): {model_path}")
    else:
        # XGBoost and others: use pickle (already compressed internally)
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        print(f"  Model: {model_path}")

    # Export scalers (dictionary with both scalers)
    scalers_path = MODELS_DIR / f"battle_winner_scalers_{version}.pkl"
    with open(scalers_path, 'wb') as f:
        pickle.dump(scalers, f)
    print(f"  Scalers: {scalers_path}")

    # Export metadata
    metadata = {
        'model_type': 'XGBClassifier',
        'version': version,
        'trained_at': datetime.now().isoformat(),
        'feature_columns': feature_columns,
        'n_features': len(feature_columns),
        'hyperparameters': best_params,
        'metrics': metrics,
        'random_seed': RANDOM_SEED,
        'grid_search_used': grid_used,
    }

    metadata_path = MODELS_DIR / f"battle_winner_metadata_{version}.pkl"
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)
    print(f"  Metadata: {metadata_path}")

    print(f"\n✅ Model artifacts exported to: {MODELS_DIR}")
    return model_path


def export_features(X_train, X_test, y_train, y_test):
    """Export feature-engineered datasets for reproducibility."""
    print("\nExporting feature-engineered datasets...")

    FEATURES_DIR.mkdir(parents=True, exist_ok=True)

    # Export features
    X_train.to_parquet(FEATURES_DIR / "X_train.parquet", index=False, engine='pyarrow')
    X_test.to_parquet(FEATURES_DIR / "X_test.parquet", index=False, engine='pyarrow')

    # Export targets
    y_train.to_frame('winner').to_parquet(FEATURES_DIR / "y_train.parquet", index=False, engine='pyarrow')
    y_test.to_frame('winner').to_parquet(FEATURES_DIR / "y_test.parquet", index=False, engine='pyarrow')

    print(f"  Features exported to: {FEATURES_DIR}")


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

    # Set global paths based on dataset version
    global DATA_DIR, PROCESSED_DIR, FEATURES_DIR
    DATA_DIR = DATA_DIR_V2 if args.dataset_version == 'v2' else DATA_DIR_V1
    PROCESSED_DIR = DATA_DIR / "processed"
    FEATURES_DIR = DATA_DIR / "features"

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

        # Feature engineering
        X_train, X_test, y_train, y_test, scalers, feature_columns = engineer_features(
            df_train, df_test
        )

        # Train model
        model, best_params = train_xgboost(
            X_train, y_train, use_gridsearch=args.use_gridsearch, grid_type=args.grid_type)

        # Evaluate
        metrics = evaluate_model(model, X_train, X_test, y_train, y_test)

        # Export model artifacts
        model_path = export_model(
            model,
            scalers,
            feature_columns,
            metrics,
            version=args.version,
            best_params=best_params,
            grid_used=args.use_gridsearch,
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
            export_features(X_train, X_test, y_train, y_test)

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
