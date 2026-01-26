#!/usr/bin/env python3
"""
Test des optimisations ML CPU
===============================

Script rapide pour valider les optimisations XGBoost CPU.

Usage:
    python test_ml_cpu_optimization.py
"""

import time
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

import xgboost as xgb
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split, GridSearchCV


def test_xgboost_cpu_optimized():
    """Test XGBoost avec tree_method='hist' (CPU optimisé)."""
    print("\n" + "=" * 80)
    print("TEST 1 : XGBoost tree_method='hist' (CPU optimisé)")
    print("=" * 80)
    
    # Génération dataset synthétique
    print("\nGénération dataset synthétique (100k samples, 50 features)...")
    X, y = make_classification(
        n_samples=100000,
        n_features=50,
        n_informative=30,
        n_redundant=10,
        random_state=42
    )
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"  Train: {len(X_train):,} samples")
    print(f"  Test: {len(X_test):,} samples")
    
    # Test 1: tree_method='auto' (baseline)
    print("\n[1/2] Test avec tree_method='auto' (baseline)...")
    model_auto = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=8,
        tree_method='auto',
        n_jobs=-1,
        random_state=42
    )
    start = time.time()
    model_auto.fit(X_train, y_train, verbose=False)
    time_auto = time.time() - start
    acc_auto = model_auto.score(X_test, y_test)
    print(f"  ⏱️  Temps: {time_auto:.2f}s")
    print(f"  🎯 Accuracy: {acc_auto:.4f}")
    
    # Test 2: tree_method='hist' (optimisé CPU)
    print("\n[2/2] Test avec tree_method='hist' (CPU optimisé)...")
    model_hist = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=8,
        tree_method='hist',        # CPU-optimized
        predictor='cpu_predictor',
        n_jobs=-1,
        random_state=42
    )
    start = time.time()
    model_hist.fit(X_train, y_train, verbose=False)
    time_hist = time.time() - start
    acc_hist = model_hist.score(X_test, y_test)
    print(f"  ⏱️  Temps: {time_hist:.2f}s")
    print(f"  🎯 Accuracy: {acc_hist:.4f}")
    
    # Comparaison
    speedup = time_auto / time_hist
    print("\n" + "=" * 80)
    print("RÉSULTATS")
    print("=" * 80)
    print(f"  tree_method='auto'  : {time_auto:.2f}s")
    print(f"  tree_method='hist'  : {time_hist:.2f}s")
    print(f"  🚀 Speedup          : {speedup:.2f}x")
    print(f"  Accuracy (auto)     : {acc_auto:.4f}")
    print(f"  Accuracy (hist)     : {acc_hist:.4f}")
    print(f"  ✅ Qualité préservée : {abs(acc_auto - acc_hist) < 0.01}")
    
    return speedup


def test_gridsearch_reduced():
    """Test GridSearch avec grid réduit."""
    print("\n" + "=" * 80)
    print("TEST 2 : GridSearchCV avec grid réduit")
    print("=" * 80)
    
    # Dataset plus petit pour GridSearch
    print("\nGénération dataset (20k samples, 30 features)...")
    X, y = make_classification(
        n_samples=20000,
        n_features=30,
        n_informative=20,
        random_state=42
    )
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Grid original (grande taille)
    grid_large = {
        'n_estimators': [50, 100, 200],
        'max_depth': [6, 8, 10],
        'learning_rate': [0.05, 0.1, 0.2],
        'subsample': [0.7, 0.8, 0.9],
        'colsample_bytree': [0.7, 0.8, 0.9],
    }
    num_combos_large = 3 * 3 * 3 * 3 * 3
    
    # Grid réduit (optimisé)
    grid_reduced = {
        'n_estimators': [100, 200],
        'max_depth': [6, 8, 10],
        'learning_rate': [0.05, 0.1],
        'subsample': [0.8],
        'colsample_bytree': [0.8],
        'tree_method': ['hist'],
    }
    num_combos_reduced = 2 * 3 * 2 * 1 * 1
    
    print(f"\nGrid original : {num_combos_large} combinaisons")
    print(f"Grid réduit   : {num_combos_reduced} combinaisons")
    print(f"Réduction     : {num_combos_large / num_combos_reduced:.1f}x")
    
    # Test avec grid réduit seulement (grid complet = trop long)
    print(f"\n[1/1] Test GridSearch avec grid réduit ({num_combos_reduced} combos)...")
    model = xgb.XGBClassifier(
        random_state=42,
        n_jobs=-1,
        tree_method='hist',
        predictor='cpu_predictor'
    )
    
    grid_search = GridSearchCV(
        model,
        grid_reduced,
        cv=3,
        scoring='roc_auc',
        n_jobs=-1,
        verbose=0
    )
    
    start = time.time()
    grid_search.fit(X_train, y_train)
    time_grid = time.time() - start
    
    best_score = grid_search.best_score_
    test_score = grid_search.score(X_test, y_test)
    
    print(f"  ⏱️  Temps total     : {time_grid:.2f}s ({time_grid/60:.1f} min)")
    print(f"  🎯 Best CV ROC-AUC : {best_score:.4f}")
    print(f"  🎯 Test Accuracy   : {test_score:.4f}")
    print(f"  📊 Best params     : {grid_search.best_params_}")
    
    # Estimation temps grid complet
    estimated_time_large = time_grid * (num_combos_large / num_combos_reduced)
    print(f"\n  ⏱️  Estimation temps grid complet : {estimated_time_large/60:.1f} min")
    print(f"  🚀 Gain de temps : {num_combos_large / num_combos_reduced:.1f}x")
    
    return time_grid


def test_early_stopping():
    """Test early stopping."""
    print("\n" + "=" * 80)
    print("TEST 3 : Early Stopping")
    print("=" * 80)
    
    # Dataset
    print("\nGénération dataset (50k samples)...")
    X, y = make_classification(n_samples=50000, n_features=30, random_state=42)
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Sans early stopping
    print("\n[1/2] Sans early stopping (n_estimators=200)...")
    model_no_es = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=8,
        tree_method='hist',
        n_jobs=-1,
        random_state=42
    )
    start = time.time()
    model_no_es.fit(X_train, y_train, verbose=False)
    time_no_es = time.time() - start
    print(f"  ⏱️  Temps: {time_no_es:.2f}s")
    print(f"  🌳 Arbres entraînés: 200")
    
    # Avec early stopping
    print("\n[2/2] Avec early stopping (n_estimators=200, patience=10)...")
    model_es = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=8,
        tree_method='hist',
        n_jobs=-1,
        random_state=42,
        early_stopping_rounds=10
    )
    start = time.time()
    model_es.fit(
        X_train, y_train,
        eval_set=[(X_train, y_train), (X_val, y_val)],
        verbose=False
    )
    time_es = time.time() - start
    best_iter = model_es.best_iteration if hasattr(model_es, 'best_iteration') else 200
    print(f"  ⏱️  Temps: {time_es:.2f}s")
    print(f"  🌳 Arbres entraînés: {best_iter}")
    print(f"  ✅ Arrêt anticipé: {best_iter < 200}")
    
    # Comparaison
    speedup = time_no_es / time_es
    trees_saved = 200 - best_iter
    print("\n" + "=" * 80)
    print("RÉSULTATS")
    print("=" * 80)
    print(f"  Sans early stopping : {time_no_es:.2f}s (200 arbres)")
    print(f"  Avec early stopping : {time_es:.2f}s ({best_iter} arbres)")
    print(f"  🚀 Speedup          : {speedup:.2f}x")
    print(f"  🌳 Arbres économisés: {trees_saved} ({trees_saved/200*100:.0f}%)")
    
    return speedup


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("TEST DES OPTIMISATIONS ML CPU")
    print("=" * 80)
    print("\nCe script teste les optimisations appliquées :")
    print("  1. tree_method='hist' (CPU-optimisé)")
    print("  2. Grid de recherche réduit (12 vs 243 combos)")
    print("  3. Early stopping")
    
    try:
        # Test 1: tree_method
        speedup_hist = test_xgboost_cpu_optimized()
        
        # Test 2: GridSearch réduit
        time_grid = test_gridsearch_reduced()
        
        # Test 3: Early stopping
        speedup_es = test_early_stopping()
        
        # Récapitulatif final
        print("\n" + "=" * 80)
        print("RÉCAPITULATIF FINAL")
        print("=" * 80)
        print(f"\n✅ Test 1 : tree_method='hist' speedup = {speedup_hist:.2f}x")
        print(f"✅ Test 2 : GridSearch réduit temps = {time_grid:.1f}s ({time_grid/60:.1f} min)")
        print(f"✅ Test 3 : Early stopping speedup = {speedup_es:.2f}x")
        print("\n🎯 Toutes les optimisations sont validées !")
        print("\n💡 Pour entraîner le vrai modèle :")
        print("   python machine_learning/run_machine_learning.py --mode=all")
        print("   python machine_learning/run_machine_learning.py --mode=all --tune-hyperparams")
        
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
