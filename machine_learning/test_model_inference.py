#!/usr/bin/env python3
"""
Test Model Inference
====================

Quick script to verify that the trained model can be loaded and used for predictions.
"""

import pickle
from pathlib import Path

import pandas as pd

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = PROJECT_ROOT / "models"
FEATURES_DIR = PROJECT_ROOT / "data" / "ml" / "battle_winner" / "features"


def load_model():
    """Load trained model, scalers, and metadata."""
    print("Loading model artifacts...")

    model_path = MODELS_DIR / "battle_winner_model_v1.pkl"
    scalers_path = MODELS_DIR / "battle_winner_scalers_v1.pkl"
    metadata_path = MODELS_DIR / "battle_winner_metadata.pkl"

    with open(model_path, 'rb') as f:
        model = pickle.load(f)

    with open(scalers_path, 'rb') as f:
        scalers = pickle.load(f)

    with open(metadata_path, 'rb') as f:
        metadata = pickle.load(f)

    print(f"  ✅ Model: {metadata['model_type']}")
    print(f"  ✅ Version: {metadata['version']}")
    print(f"  ✅ Features: {metadata['n_features']}")
    print(f"  ✅ Test Accuracy: {metadata['metrics']['test_accuracy']:.4f}")

    return model, scalers, metadata


def test_prediction():
    """Test prediction on a few samples."""
    print("\nTesting predictions...")

    # Load model
    model, scalers, metadata = load_model()

    # Load test features
    X_test = pd.read_parquet(FEATURES_DIR / "X_test.parquet")
    y_test = pd.read_parquet(FEATURES_DIR / "y_test.parquet")

    print(f"\nLoaded test set: {X_test.shape}")

    # Make predictions on first 5 samples
    n_samples = 5
    X_sample = X_test.head(n_samples)
    y_sample = y_test.head(n_samples)

    predictions = model.predict(X_sample)
    probabilities = model.predict_proba(X_sample)

    print(f"\nPredictions for first {n_samples} samples:")
    print("=" * 60)
    for i in range(n_samples):
        true_label = y_sample.iloc[i]['winner']
        pred_label = predictions[i]
        prob = probabilities[i]

        result = "✅" if true_label == pred_label else "❌"
        winner_name = "Pokémon A" if pred_label == 1 else "Pokémon B"

        print(f"Sample {i+1}: {result}")
        print(f"  True: {'A wins' if true_label == 1 else 'B wins'}")
        print(f"  Predicted: {winner_name} wins")
        print(f"  Confidence: {prob[pred_label]*100:.1f}%")
        print()


if __name__ == "__main__":
    print("=" * 60)
    print("MODEL INFERENCE TEST")
    print("=" * 60)

    test_prediction()

    print("=" * 60)
    print("✅ TEST COMPLETE")
    print("=" * 60)
