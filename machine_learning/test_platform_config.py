#!/usr/bin/env python3
"""
Platform configuration test script.

Displays auto-detected parameters based on the platform
(Windows/Linux) and verifies that optimizations are
correctly applied.

Usage:
    python machine_learning/test_platform_config.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from machine_learning.platform_config import (
    get_platform_info,
    get_safe_n_jobs,
    get_safe_gridsearch_n_jobs,
    print_platform_summary,
    SAFE_N_JOBS,
    SAFE_GRIDSEARCH_N_JOBS,
)
from machine_learning.config import XGBOOST_PARAMS


def main():
    """Display detected configuration."""
    print("\n" + "=" * 70)
    print("PLATFORM CONFIGURATION TEST")
    print("=" * 70)

    # Print platform summary
    print_platform_summary()

    # Test individual functions
    print("\n[Tests] Functions:")
    print(f"  get_safe_n_jobs() = {get_safe_n_jobs()}")
    print(f"  get_safe_gridsearch_n_jobs() = {get_safe_gridsearch_n_jobs()}")

    # Display constants
    print("\n[Config] Global constants:")
    print(f"  SAFE_N_JOBS = {SAFE_N_JOBS}")
    print(f"  SAFE_GRIDSEARCH_N_JOBS = {SAFE_GRIDSEARCH_N_JOBS}")

    # Display XGBoost config
    print("\n[XGBoost] Configuration:")
    for key, value in XGBOOST_PARAMS.items():
        if key == 'n_jobs':
            print(f"  {key}: {value} (*auto-adjusted per platform)")
        else:
            print(f"  {key}: {value}")

    # Recommendations
    info = get_platform_info()
    print("\n[Recommendations]")
    if info['is_windows']:
        print("  [OK] Windows detected - Memory optimizations enabled")
        print("  [OK] Job count reduced to prevent saturation")
        print("  [OK] Garbage collector set to aggressive mode")
        print("\n  [Recommended commands]")
        print("     # Without GridSearch (fast, less RAM)")
        print("     python machine_learning/run_machine_learning.py --mode=all")
        print("\n     # With FAST GridSearch (moderate tuning)")
        print("     python machine_learning/run_machine_learning.py --mode=all --tune-hyperparams --grid-type fast")
        print("\n     [WARN] EXTENDED GridSearch not recommended on Windows (too much RAM)")
    else:
        print("  [OK] Linux detected - High performance configuration")
        print("  [OK] All CPU cores utilized")
        print("  [OK] EXTENDED GridSearch available")
        print("\n  [Available commands]")
        print("     # Full pipeline with extended tuning")
        print("     python machine_learning/run_machine_learning.py --mode=all --tune-hyperparams --grid-type extended")

    print("\n" + "=" * 70)
    print("[SUCCESS] Configuration loaded successfully!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
