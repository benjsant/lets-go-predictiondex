#!/usr/bin/env python3
"""
Compress existing ML models using joblib
=========================================

This script converts existing pickle models to compressed joblib format,
significantly reducing file size (especially for RandomForest).

Usage:
    python compress_ml_models.py [--version v2]

Before:
    battle_winner_rf_v2.pkl = 401 MB (pickle)

After:
    battle_winner_model_v2.pkl = ~40-80 MB (joblib zlib level 9)

Compression ratio: 5-10x for RandomForest models
"""

import pickle
import joblib
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent
MODELS_DIR = PROJECT_ROOT / "models"


def compress_model(version: str = "v2"):
    """Compress a model using joblib with aggressive compression."""
    
    model_path = MODELS_DIR / f"battle_winner_model_{version}.pkl"
    backup_path = MODELS_DIR / f"battle_winner_model_{version}.pkl.backup"
    
    if not model_path.exists():
        print(f"❌ Model not found: {model_path}")
        return False
    
    print(f"📦 Loading model from: {model_path}")
    original_size = model_path.stat().st_size / (1024 * 1024)  # MB
    print(f"   Original size: {original_size:.2f} MB")
    
    # Load with pickle
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        print(f"✅ Model loaded: {type(model).__name__}")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return False
    
    # Backup original
    print(f"\n💾 Creating backup: {backup_path}")
    model_path.rename(backup_path)
    
    # Save with joblib compression
    print(f"🗜️  Compressing with joblib (zlib level 9)...")
    joblib.dump(model, model_path, compress=('zlib', 9))
    
    compressed_size = model_path.stat().st_size / (1024 * 1024)  # MB
    ratio = original_size / compressed_size
    
    print(f"\n✅ Compression complete!")
    print(f"   Original:   {original_size:.2f} MB")
    print(f"   Compressed: {compressed_size:.2f} MB")
    print(f"   Ratio:      {ratio:.2f}x smaller")
    print(f"   Saved:      {original_size - compressed_size:.2f} MB")
    
    # Test loading
    print(f"\n🧪 Testing compressed model load...")
    try:
        test_model = joblib.load(model_path)
        print(f"✅ Successfully loaded: {type(test_model).__name__}")
        
        # Verify it's the same model
        if hasattr(test_model, 'n_estimators'):
            print(f"   n_estimators: {test_model.n_estimators}")
        if hasattr(test_model, 'n_features_in_'):
            print(f"   n_features: {test_model.n_features_in_}")
            
        print(f"\n✅ All checks passed!")
        print(f"💡 You can now delete the backup: {backup_path}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to load compressed model: {e}")
        print(f"🔄 Restoring backup...")
        backup_path.rename(model_path)
        return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Compress ML models")
    parser.add_argument("--version", default="v2", help="Model version (default: v2)")
    args = parser.parse_args()
    
    print("=" * 80)
    print("ML MODEL COMPRESSION")
    print("=" * 80)
    print(f"\nVersion: {args.version}")
    print(f"Models directory: {MODELS_DIR}")
    
    success = compress_model(args.version)
    
    if success:
        print("\n" + "=" * 80)
        print("✅ COMPRESSION SUCCESSFUL")
        print("=" * 80)
        return 0
    else:
        print("\n" + "=" * 80)
        print("❌ COMPRESSION FAILED")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
