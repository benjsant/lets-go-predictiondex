#!/usr/bin/env python3
"""
Train Battle Winner Prediction Model - Production Script
=========================================================

This script automates the complete ML pipeline:
1. Load train/test datasets from parquet files
2. Feature engineering (one-hot encoding, derived features, normalization)
3. Train XGBoost model (best performer: 94.24% accuracy)
4. Export trained model, scalers, and metadata

Usage:
    python machine_learning/train_model.py

Output:
    - models/battle_winner_model_v1.pkl (XGBoost model)
    - models/battle_winner_scaler_v1.pkl (StandardScaler)
    - models/battle_winner_metadata.pkl (feature columns, performance metrics)
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
import pickle

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.metrics import classification_report, confusion_matrix
import xgboost as xgb

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "ml" / "battle_winner"
PROCESSED_DIR = DATA_DIR / "processed"
FEATURES_DIR = DATA_DIR / "features"
MODELS_DIR = PROJECT_ROOT / "models"

# Random seed for reproducibility
RANDOM_SEED = 42

# XGBoost hyperparameters (from notebook 03)
XGBOOST_PARAMS = {
    'n_estimators': 100,
    'max_depth': 8,
    'learning_rate': 0.1,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'random_state': RANDOM_SEED,
    'n_jobs': -1,
    'eval_metric': 'logloss',
}


def load_datasets():
    """Load train and test datasets from parquet files."""
    print("Loading datasets...")

    train_path = PROCESSED_DIR / "train.parquet"
    test_path = PROCESSED_DIR / "test.parquet"

    if not train_path.exists():
        raise FileNotFoundError(
            f"Train dataset not found: {train_path}\n"
            f"Please run: POSTGRES_HOST=localhost python machine_learning/build_battle_winner_dataset.py"
        )

    if not test_path.exists():
        raise FileNotFoundError(f"Test dataset not found: {test_path}")

    df_train = pd.read_parquet(train_path)
    df_test = pd.read_parquet(test_path)

    print(f"  Train: {len(df_train):,} samples")
    print(f"  Test: {len(df_test):,} samples")

    return df_train, df_test


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
    columns_to_drop = categorical_features + id_features
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


def train_xgboost(X_train, y_train):
    """Train XGBoost classifier."""
    print("\nTraining XGBoost model...")
    print(f"  Hyperparameters: {XGBOOST_PARAMS}")

    model = xgb.XGBClassifier(**XGBOOST_PARAMS)
    model.fit(X_train, y_train, verbose=False)

    print("  Training complete")
    return model


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


def export_model(model, scalers, feature_columns, metrics):
    """Export trained model, scalers, and metadata."""
    print("\nExporting model artifacts...")

    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # Export model
    model_path = MODELS_DIR / "battle_winner_model_v1.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"  Model: {model_path}")

    # Export scalers (dictionary with both scalers)
    scalers_path = MODELS_DIR / "battle_winner_scalers_v1.pkl"
    with open(scalers_path, 'wb') as f:
        pickle.dump(scalers, f)
    print(f"  Scalers: {scalers_path}")

    # Export metadata
    metadata = {
        'model_type': 'XGBClassifier',
        'version': 'v1',
        'trained_at': datetime.now().isoformat(),
        'feature_columns': feature_columns,
        'n_features': len(feature_columns),
        'hyperparameters': XGBOOST_PARAMS,
        'metrics': metrics,
        'random_seed': RANDOM_SEED,
    }

    metadata_path = MODELS_DIR / "battle_winner_metadata.pkl"
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)
    print(f"  Metadata: {metadata_path}")

    print(f"\n✅ Model artifacts exported to: {MODELS_DIR}")


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
    args = parser.parse_args()

    print("=" * 60)
    print("BATTLE WINNER PREDICTION MODEL - TRAINING")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Random Seed: {RANDOM_SEED}")

    try:
        # Load data
        df_train, df_test = load_datasets()

        # Feature engineering
        X_train, X_test, y_train, y_test, scalers, feature_columns = engineer_features(
            df_train, df_test
        )

        # Train model
        model = train_xgboost(X_train, y_train)

        # Evaluate
        metrics = evaluate_model(model, X_train, X_test, y_train, y_test)

        # Export model artifacts
        export_model(model, scalers, feature_columns, metrics)

        # Export features (optional)
        if not args.skip_export_features:
            export_features(X_train, X_test, y_train, y_test)

        print("\n" + "=" * 60)
        print("TRAINING COMPLETE")
        print("=" * 60)
        print(f"\n✅ Test Accuracy: {metrics['test_accuracy']*100:.2f}%")
        print(f"✅ Test ROC-AUC: {metrics['test_roc_auc']:.4f}")

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
