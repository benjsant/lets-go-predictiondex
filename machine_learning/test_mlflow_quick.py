#!/usr/bin/env python3
"""
Quick test of MLflow integration
"""
from machine_learning.mlflow_integration import get_mlflow_tracker
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# Test
tracker = get_mlflow_tracker("test_quick")
tracker.start_run(run_name="quick_test")
tracker.log_params({'test': 'ok'})
tracker.log_metrics({'accuracy': 0.95})
print("✅ MLflow test réussi!")
print("🔗 http://localhost:5000")
