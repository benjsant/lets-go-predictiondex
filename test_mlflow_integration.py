#!/usr/bin/env python3
"""
Test MLflow integration for Pokemon Battle ML Pipeline
Validates C13 (MLOps) - Experiment tracking
"""

import sys
from pathlib import Path

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from machine_learning.mlflow_integration import get_mlflow_tracker

def test_mlflow_basic():
    """Test basic MLflow tracking operations."""
    print("\n🧪 Test 1: Initialize MLflow tracker")
    tracker = get_mlflow_tracker("test_pokemon_battle")
    print("✅ Tracker initialized")
    
    print("\n🧪 Test 2: Start MLflow run")
    tracker.start_run(run_name="test_integration_full")
    print("✅ Run started")
    
    print("\n🧪 Test 3: Log parameters")
    tracker.log_params({
        'model_type': 'XGBoost',
        'n_estimators': 100,
        'max_depth': 8,
        'learning_rate': 0.1,
    })
    print("✅ Parameters logged")
    
    print("\n🧪 Test 4: Log metrics")
    tracker.log_metrics({
        'train_accuracy': 0.987,
        'test_accuracy': 0.944,
        'test_f1': 0.948,
        'test_roc_auc': 0.982,
        'overfitting': 0.043,
    })
    print("✅ Metrics logged")
    
    print("\n🧪 Test 5: Log dataset info")
    tracker.log_dataset_info(
        train_samples=10000,
        test_samples=2500,
        num_features=45
    )
    print("✅ Dataset info logged")
    
    print("\n✅ All tests passed!")
    print("\n🔗 View results: http://localhost:5000")
    print("   Experiment: test_pokemon_battle")
    print("   Run: test_integration_full")

if __name__ == "__main__":
    test_mlflow_basic()
