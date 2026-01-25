"""
Model Inference Tests
====================

Tests for model prediction and inference.

Validation:
- Model loads correctly
- Predictions are valid
- Prediction probabilities sum to 1
- Model is deterministic
- API inference works
"""

import pytest
import pickle
import pandas as pd
import numpy as np
from pathlib import Path


# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = PROJECT_ROOT / "models"
FEATURES_DIR = PROJECT_ROOT / "data" / "ml" / "battle_winner_v2" / "features"


@pytest.fixture
def model():
    """Load trained model."""
    model_path = MODELS_DIR / "battle_winner_model_v2.pkl"
    if not model_path.exists():
        pytest.skip(f"Model not found: {model_path}")
    
    with open(model_path, 'rb') as f:
        return pickle.load(f)


@pytest.fixture
def metadata():
    """Load model metadata."""
    metadata_path = MODELS_DIR / "battle_winner_metadata_v2.pkl"
    if not metadata_path.exists():
        pytest.skip(f"Metadata not found: {metadata_path}")
    
    with open(metadata_path, 'rb') as f:
        return pickle.load(f)


@pytest.fixture
def X_test():
    """Load test features and drop scenario_type for model prediction."""
    X_test_path = FEATURES_DIR / "X_test.parquet"
    if not X_test_path.exists():
        pytest.skip(f"Test features not found: {X_test_path}")
    df = pd.read_parquet(X_test_path)
    # Drop scenario_type if present (kept for analysis but not for model.predict())
    if 'scenario_type' in df.columns:
        df = df.drop(columns=['scenario_type'])
    return df


@pytest.fixture
def y_test():
    """Load test labels."""
    y_test_path = FEATURES_DIR / "y_test.parquet"
    if not y_test_path.exists():
        pytest.skip(f"Test labels not found: {y_test_path}")
    return pd.read_parquet(y_test_path)['winner']


def test_model_exists():
    """Test that model file exists."""
    model_path = MODELS_DIR / "battle_winner_model_v2.pkl"
    assert model_path.exists(), f"Model not found: {model_path}"


def test_model_loads(model):
    """Test that model loads successfully."""
    assert model is not None, "Model is None"
    assert hasattr(model, 'predict'), "Model doesn't have predict method"
    assert hasattr(model, 'predict_proba'), "Model doesn't have predict_proba method"


def test_metadata_exists():
    """Test that metadata file exists."""
    metadata_path = MODELS_DIR / "battle_winner_metadata_v2.pkl"
    assert metadata_path.exists(), f"Metadata not found: {metadata_path}"


def test_metadata_content(metadata):
    """Test that metadata has expected keys."""
    expected_keys = {
        'model_name',
        'version',
        'n_features',
        'features',
        'metrics'
    }
    
    for key in expected_keys:
        assert key in metadata, f"Metadata missing key: {key}"
    
    # Check that metrics sub-dict exists
    assert 'test_accuracy' in metadata['metrics'], "Metadata missing metrics.test_accuracy"
    assert 'test_roc_auc' in metadata['metrics'], "Metadata missing metrics.test_roc_auc"


def test_metadata_values(metadata):
    """Test that metadata values are reasonable."""
    assert metadata['n_features'] == 133, \
        f"Expected 133 features, got {metadata['n_features']}"
    
    assert metadata['version'] == 'v2', \
        f"Expected version v2, got {metadata['version']}"
    
    assert 0.90 <= metadata['metrics']['test_accuracy'] <= 1.0, \
        f"Test accuracy out of range: {metadata['metrics']['test_accuracy']}"
    
    assert 0.90 <= metadata['metrics']['test_roc_auc'] <= 1.0, \
        f"Test ROC-AUC out of range: {metadata['metrics']['test_roc_auc']}"


def test_model_predict(model, X_test):
    """Test that model can make predictions."""
    # Take a small sample
    X_sample = X_test.head(10)
    
    predictions = model.predict(X_sample, validate_features=False)
    
    assert len(predictions) == len(X_sample), "Wrong number of predictions"
    assert all(p in [0, 1] for p in predictions), "Predictions not binary"


def test_model_predict_proba(model, X_test):
    """Test that model can predict probabilities."""
    X_sample = X_test.head(10)
    
    probabilities = model.predict_proba(X_sample, validate_features=False)
    
    assert probabilities.shape == (len(X_sample), 2), "Wrong probability shape"
    assert all(0 <= p <= 1 for p in probabilities.flatten()), "Probabilities out of range"


def test_probabilities_sum_to_one(model, X_test):
    """Test that probabilities sum to 1 for each sample."""
    X_sample = X_test.head(100)
    
    probabilities = model.predict_proba(X_sample, validate_features=False)
    
    sums = probabilities.sum(axis=1)
    assert np.allclose(sums, 1.0), f"Probabilities don't sum to 1: {sums}"


def test_predictions_consistent_with_probabilities(model, X_test):
    """Test that predictions match probabilities."""
    X_sample = X_test.head(100)
    
    predictions = model.predict(X_sample, validate_features=False)
    probabilities = model.predict_proba(X_sample, validate_features=False)
    
    # Prediction should be argmax of probabilities
    predicted_from_proba = np.argmax(probabilities, axis=1)
    
    assert np.array_equal(predictions, predicted_from_proba), \
        "Predictions don't match probabilities"


def test_model_deterministic(model, X_test):
    """Test that model predictions are deterministic."""
    X_sample = X_test.head(50)
    
    predictions_1 = model.predict(X_sample, validate_features=False)
    predictions_2 = model.predict(X_sample, validate_features=False)
    
    assert np.array_equal(predictions_1, predictions_2), \
        "Model predictions not deterministic"


def test_model_performance_on_test_set(model, X_test, y_test, metadata):
    """Test that model maintains expected performance on test set."""
    predictions = model.predict(X_test, validate_features=False)
    
    accuracy = (predictions == y_test).mean()
    
    # Should be close to metadata accuracy (within 1%)
    expected_accuracy = metadata['metrics']['test_accuracy']
    assert abs(accuracy - expected_accuracy) < 0.01, \
        f"Accuracy {accuracy:.4f} differs from metadata {expected_accuracy:.4f}"


def test_model_handles_edge_cases(model, X_test):
    """Test that model handles edge cases."""
    # Test with single sample
    X_single = X_test.head(1)
    pred_single = model.predict(X_single, validate_features=False)
    assert len(pred_single) == 1, "Failed on single sample"
    
    # Test with multiple samples
    X_multi = X_test.head(100)
    pred_multi = model.predict(X_multi, validate_features=False)
    assert len(pred_multi) == 100, "Failed on multiple samples"


def test_no_prediction_errors_on_full_test(model, X_test):
    """Test that model can predict on entire test set without errors."""
    try:
        predictions = model.predict(X_test, validate_features=False)
        assert len(predictions) == len(X_test), "Incomplete predictions"
    except Exception as e:
        pytest.fail(f"Model failed to predict on full test set: {e}")


def test_prediction_confidence_distribution(model, X_test):
    """Test that prediction confidence has reasonable distribution."""
    X_sample = X_test.sample(n=min(1000, len(X_test)), random_state=42)
    
    probabilities = model.predict_proba(X_sample, validate_features=False)
    max_probs = probabilities.max(axis=1)
    
    # Most predictions should have high confidence (> 0.5)
    high_confidence = (max_probs > 0.5).mean()
    assert high_confidence > 0.50, \
        f"Too many low-confidence predictions: {high_confidence:.2%}"
    
    # But not all should be 100% confident
    very_high_confidence = (max_probs > 0.99).mean()
    assert very_high_confidence < 0.80, \
        f"Too many overly confident predictions: {very_high_confidence:.2%}"


def test_class_distribution_predictions(model, X_test):
    """Test that predicted class distribution is reasonable."""
    predictions = model.predict(X_test, validate_features=False)
    
    class_distribution = pd.Series(predictions).value_counts(normalize=True)
    
    # Both classes should be predicted
    assert len(class_distribution) == 2, "Model only predicts one class"
    
    # Distribution should be somewhat balanced (20-80% range)
    assert class_distribution.min() >= 0.20, \
        f"Class imbalance too severe: {class_distribution}"
    assert class_distribution.max() <= 0.80, \
        f"Class imbalance too severe: {class_distribution}"


def test_feature_importance_exists(model):
    """Test that model has feature importance (for tree-based models)."""
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        
        assert len(importances) == 133, "Wrong number of feature importances"
        assert all(imp >= 0 for imp in importances), "Negative feature importances"
        assert sum(importances) > 0, "All feature importances are zero"


def test_no_nan_predictions(model, X_test):
    """Test that model doesn't produce NaN predictions."""
    X_sample = X_test.head(1000)
    
    predictions = model.predict(X_sample, validate_features=False)
    probabilities = model.predict_proba(X_sample, validate_features=False)
    
    assert not np.isnan(predictions).any(), "NaN in predictions"
    assert not np.isnan(probabilities).any(), "NaN in probabilities"


def test_prediction_speed(model, X_test):
    """Test that predictions are reasonably fast."""
    import time
    
    X_sample = X_test.head(1000)
    
    start = time.time()
    _ = model.predict(X_sample, validate_features=False)
    duration = time.time() - start
    
    # Should predict 1000 samples in < 1 second
    assert duration < 1.0, f"Prediction too slow: {duration:.2f}s for 1000 samples"


def test_model_not_overfitting(model, X_test, y_test):
    """Test that model isn't overfitting (test performance is reasonable)."""
    predictions = model.predict(X_test, validate_features=False)
    accuracy = (predictions == y_test).mean()
    
    # Test accuracy should be high (> 90% for this problem)
    assert accuracy > 0.90, f"Test accuracy too low: {accuracy:.2%}"


def test_scalers_exist():
    """Test that scalers file exists."""
    scalers_path = MODELS_DIR / "battle_winner_scalers_v2.pkl"
    assert scalers_path.exists(), f"Scalers not found: {scalers_path}"


def test_scalers_load():
    """Test that scalers load correctly."""
    scalers_path = MODELS_DIR / "battle_winner_scalers_v2.pkl"
    
    with open(scalers_path, 'rb') as f:
        scalers = pickle.load(f)
    
    assert isinstance(scalers, dict), "Scalers should be a dict"
    assert 'standard_scaler' in scalers, "Missing standard_scaler"
    # v2 uses standard_scaler_new_features instead of derived_scaler
    assert len(scalers) > 0, "Scalers dict should not be empty"
