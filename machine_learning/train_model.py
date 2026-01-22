#!/usr/bin/env python3
"""
Train Battle Winner Prediction Model - Adapted for PredictionDex LGPE
====================================================================

Pipeline:
1) Chargement des jeux train/test (parquet)
2) Feature engineering (encodage, features dérivées, normalisation)
3) Entraînement XGBoost, option GridSearchCV
4) Export du modèle, des scalers et des métadonnées versionnées
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
from sklearn.model_selection import GridSearchCV, StratifiedKFold
import xgboost as xgb

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "ml" / "battle_winner"
PROCESSED_DIR = DATA_DIR / "processed"
FEATURES_DIR = DATA_DIR / "features"
MODELS_DIR = PROJECT_ROOT / "models"

RANDOM_SEED = 42

# XGBoost defaults
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

# GridSearch small grid
XGBOOST_PARAM_GRID = {
    'n_estimators': [120, 200],
    'max_depth': [6, 8],
    'learning_rate': [0.05, 0.1],
    'subsample': [0.8, 1.0],
    'colsample_bytree': [0.8, 1.0],
}

# ------------------ DATA LOADING ------------------ #
def load_datasets():
    train_path = PROCESSED_DIR / "train.parquet"
    test_path = PROCESSED_DIR / "test.parquet"
    if not train_path.exists() or not test_path.exists():
        raise FileNotFoundError(
            f"Dataset missing. Run build_battle_winner_dataset.py first."
        )
    df_train = pd.read_parquet(train_path)
    df_test = pd.read_parquet(test_path)
    print(f"Loaded datasets: Train={len(df_train):,} | Test={len(df_test):,}")
    return df_train, df_test

# ------------------ SCENARIO FILTER ------------------ #
def filter_by_scenario(df_train, df_test, scenario_type: str):
    if scenario_type == "all" or "scenario_type" not in df_train.columns:
        return df_train, df_test
    df_train_filtered = df_train[df_train["scenario_type"] == scenario_type]
    df_test_filtered = df_test[df_test["scenario_type"] == scenario_type]
    if df_train_filtered.empty or df_test_filtered.empty:
        print(f"⚠ scenario_type '{scenario_type}' empty, using full dataset.")
        return df_train, df_test
    print(f"Scenario filter '{scenario_type}': Train {len(df_train)}→{len(df_train_filtered)}, Test {len(df_test)}→{len(df_test_filtered)}")
    return df_train_filtered, df_test_filtered

# ------------------ FEATURE ENGINEERING ------------------ #
def engineer_features(df_train, df_test):
    y_train = df_train['winner']
    y_test = df_test['winner']
    
    X_train = df_train.drop(columns=['winner']).copy()
    X_test = df_test.drop(columns=['winner']).copy()
    
    # Categorical features to encode
    categorical_features = ['a_type_1','a_type_2','b_type_1','b_type_2','a_move_type','b_move_type']
    for feature in categorical_features:
        if feature in X_train.columns:
            train_dummies = pd.get_dummies(X_train[feature], prefix=feature, drop_first=False)
            test_dummies = pd.get_dummies(X_test[feature], prefix=feature, drop_first=False)
            train_dummies, test_dummies = train_dummies.align(test_dummies, join='left', axis=1, fill_value=0)
            X_train = pd.concat([X_train, train_dummies], axis=1)
            X_test = pd.concat([X_test, test_dummies], axis=1)
    
    # Drop original categorical columns & IDs
    id_features = ['pokemon_a_id','pokemon_b_id','pokemon_a_name','pokemon_b_name','a_move_name','b_move_name','scenario_type']
    drop_cols = [c for c in categorical_features + id_features if c in X_train.columns]
    X_train.drop(columns=drop_cols, inplace=True)
    X_test.drop(columns=drop_cols, inplace=True)
    
    # Normalize numerical features
    num_features = [
        'a_hp','a_attack','a_defense','a_sp_attack','a_sp_defense','a_speed',
        'b_hp','b_attack','b_defense','b_sp_attack','b_sp_defense','b_speed',
        'a_move_power','b_move_power',
        'a_total_stats','b_total_stats',
        'speed_diff','hp_diff'
    ]
    num_features = [f for f in num_features if f in X_train.columns]
    scaler = StandardScaler()
    X_train[num_features] = scaler.fit_transform(X_train[num_features])
    X_test[num_features] = scaler.transform(X_test[num_features])
    
    # Derived features
    derived = {
        'stat_ratio': df_train['a_total_stats'] / (df_train['b_total_stats'] + 1),
        'type_advantage_diff': df_train['a_move_type_mult'] - df_train['b_move_type_mult'],
        'effective_power_a': df_train['a_move_power'] * df_train['a_move_stab'] * df_train['a_move_type_mult'],
        'effective_power_b': df_train['b_move_power'] * df_train['b_move_stab'] * df_train['b_move_type_mult'],
        'effective_power_diff': None,  # will calculate after a/b
        'priority_advantage': df_train['a_move_priority'] - df_train['b_move_priority'],
    }
    df_test_derived = {
        'stat_ratio': df_test['a_total_stats'] / (df_test['b_total_stats'] + 1),
        'type_advantage_diff': df_test['a_move_type_mult'] - df_test['b_move_type_mult'],
        'effective_power_a': df_test['a_move_power'] * df_test['a_move_stab'] * df_test['a_move_type_mult'],
        'effective_power_b': df_test['b_move_power'] * df_test['b_move_stab'] * df_test['b_move_type_mult'],
        'priority_advantage': df_test['a_move_priority'] - df_test['b_move_priority'],
    }
    # Add to X
    for k, v in derived.items():
        if k == 'effective_power_diff':
            X_train[k] = X_train['effective_power_a'] - X_train['effective_power_b']
            X_test[k] = df_test_derived['effective_power_a'] - df_test_derived['effective_power_b']
        else:
            X_train[k] = v
            X_test[k] = df_test_derived[k]
    
    # Normalize derived
    derived_features = ['stat_ratio','type_advantage_diff','effective_power_a','effective_power_b','effective_power_diff','priority_advantage']
    scaler_new = StandardScaler()
    X_train[derived_features] = scaler_new.fit_transform(X_train[derived_features])
    X_test[derived_features] = scaler_new.transform(X_test[derived_features])
    
    scalers = {'standard_scaler': scaler, 'standard_scaler_new_features': scaler_new}
    
    print(f"Features engineered: {X_train.shape[1]} columns")
    return X_train, X_test, y_train, y_test, scalers, X_train.columns.tolist()

# ------------------ MODEL TRAINING ------------------ #
def train_xgboost(X_train, y_train, use_gridsearch=False):
    if use_gridsearch:
        cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=RANDOM_SEED)
        grid = GridSearchCV(xgb.XGBClassifier(**XGBOOST_PARAMS), param_grid=XGBOOST_PARAM_GRID, scoring='roc_auc', cv=cv, n_jobs=-1, verbose=1)
        grid.fit(X_train, y_train)
        print(f"Best params: {grid.best_params_}")
        return grid.best_estimator_, grid.best_params_
    else:
        model = xgb.XGBClassifier(**XGBOOST_PARAMS)
        model.fit(X_train, y_train)
        return model, XGBOOST_PARAMS

# ------------------ MODEL EVALUATION ------------------ #
def evaluate_model(model, X_train, X_test, y_train, y_test):
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    y_test_proba = model.predict_proba(X_test)[:,1]
    metrics = {
        'train_accuracy': accuracy_score(y_train, y_train_pred),
        'test_accuracy': accuracy_score(y_test, y_test_pred),
        'test_precision': precision_score(y_test, y_test_pred),
        'test_recall': recall_score(y_test, y_test_pred),
        'test_f1': f1_score(y_test, y_test_pred),
        'test_roc_auc': roc_auc_score(y_test, y_test_proba),
    }
    print(f"Test Accuracy: {metrics['test_accuracy']*100:.2f}% | ROC-AUC: {metrics['test_roc_auc']:.4f}")
    return metrics

# ------------------ EXPORT ------------------ #
def export_model(model, scalers, feature_columns, metrics, version='v1', best_params=None, grid_used=False):
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    with open(MODELS_DIR / f"battle_winner_model_{version}.pkl",'wb') as f: pickle.dump(model,f)
    with open(MODELS_DIR / f"battle_winner_scalers_{version}.pkl",'wb') as f: pickle.dump(scalers,f)
    metadata = {
        'model_type':'XGBClassifier','version':version,'trained_at':datetime.now().isoformat(),
        'feature_columns':feature_columns,'n_features':len(feature_columns),
        'hyperparameters':best_params,'metrics':metrics,'grid_search_used':grid_used
    }
    with open(MODELS_DIR / f"battle_winner_metadata_{version}.pkl",'wb') as f: pickle.dump(metadata,f)
    print(f"Model artifacts exported (version={version})")

# ------------------ MAIN ------------------ #
def main():
    parser = argparse.ArgumentParser(description="Train Battle Winner Prediction Model LGPE")
    parser.add_argument('--use-gridsearch', action='store_true', help='Enable GridSearchCV')
    parser.add_argument('--version', default='v1')
    parser.add_argument('--scenario-type', default='all')
    args = parser.parse_args()
    
    df_train, df_test = load_datasets()
    df_train, df_test = filter_by_scenario(df_train, df_test, args.scenario_type)
    X_train, X_test, y_train, y_test, scalers, feature_columns = engineer_features(df_train, df_test)
    model, best_params = train_xgboost(X_train, y_train, use_gridsearch=args.use_gridsearch)
    metrics = evaluate_model(model, X_train, X_test, y_train, y_test)
    export_model(model, scalers, feature_columns, metrics, version=args.version, best_params=best_params, grid_used=args.use_gridsearch)

if __name__ == "__main__":
    main()
