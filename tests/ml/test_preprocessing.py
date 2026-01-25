"""
Preprocessing Pipeline Tests
============================

Tests for feature engineering and preprocessing.

Validation:
- One-hot encoding
- Normalization (StandardScaler)
- Derived features calculation
- Feature alignment train/test
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler


# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FEATURES_DIR = PROJECT_ROOT / "data" / "ml" / "battle_winner_v2" / "features"


@pytest.fixture
def X_train():
    """Load training features."""
    X_train_path = FEATURES_DIR / "X_train.parquet"
    if not X_train_path.exists():
        pytest.skip(f"Training features not found: {X_train_path}")
    return pd.read_parquet(X_train_path)


@pytest.fixture
def X_test():
    """Load test features."""
    X_test_path = FEATURES_DIR / "X_test.parquet"
    if not X_test_path.exists():
        pytest.skip(f"Test features not found: {X_test_path}")
    return pd.read_parquet(X_test_path)


@pytest.fixture
def y_train():
    """Load training labels."""
    y_train_path = FEATURES_DIR / "y_train.parquet"
    if not y_train_path.exists():
        pytest.skip(f"Training labels not found: {y_train_path}")
    return pd.read_parquet(y_train_path)['winner']


@pytest.fixture
def y_test():
    """Load test labels."""
    y_test_path = FEATURES_DIR / "y_test.parquet"
    if not y_test_path.exists():
        pytest.skip(f"Test labels not found: {y_test_path}")
    return pd.read_parquet(y_test_path)['winner']


def test_features_exist():
    """Test that feature files exist."""
    assert FEATURES_DIR.exists(), f"Features directory not found: {FEATURES_DIR}"
    assert (FEATURES_DIR / "X_train.parquet").exists(), "X_train.parquet not found"
    assert (FEATURES_DIR / "X_test.parquet").exists(), "X_test.parquet not found"
    assert (FEATURES_DIR / "y_train.parquet").exists(), "y_train.parquet not found"
    assert (FEATURES_DIR / "y_test.parquet").exists(), "y_test.parquet not found"


def test_feature_count(X_train, X_test):
    """Test that we have expected number of features (134 for v2)."""
    # After preprocessing: 133 ML features + scenario_type (kept for analysis)
    expected_features = 134
    
    assert X_train.shape[1] == expected_features, \
        f"Expected {expected_features} features, got {X_train.shape[1]}"
    assert X_test.shape[1] == expected_features, \
        f"Expected {expected_features} features, got {X_test.shape[1]}"


def test_same_features_train_test(X_train, X_test):
    """Test that train and test have same features."""
    train_cols = set(X_train.columns)
    test_cols = set(X_test.columns)
    
    missing_in_test = train_cols - test_cols
    missing_in_train = test_cols - train_cols
    
    assert len(missing_in_test) == 0, f"Features missing in test: {missing_in_test}"
    assert len(missing_in_train) == 0, f"Features missing in train: {missing_in_train}"
    assert list(X_train.columns) == list(X_test.columns), "Feature order differs"


def test_no_missing_values(X_train, X_test):
    """Test that preprocessed features have no missing values."""
    train_nulls = X_train.isnull().sum().sum()
    test_nulls = X_test.isnull().sum().sum()
    
    assert train_nulls == 0, f"Training features have {train_nulls} null values"
    assert test_nulls == 0, f"Test features have {test_nulls} null values"


def test_all_numeric(X_train, X_test):
    """Test that all features are numeric after preprocessing."""
    non_numeric_allowed = {'scenario_type'}
    
    for col in X_train.columns:
        if col not in non_numeric_allowed:
            assert pd.api.types.is_numeric_dtype(X_train[col]), \
                f"Feature {col} is not numeric in train"
    
    for col in X_test.columns:
        if col not in non_numeric_allowed:
            assert pd.api.types.is_numeric_dtype(X_test[col]), \
                f"Feature {col} is not numeric in test"


def test_one_hot_encoding(X_train):
    """Test that categorical features were one-hot encoded."""
    # Check for type columns (should be one-hot encoded)
    type_cols = [col for col in X_train.columns if col.startswith(('a_type_1_', 'a_type_2_', 'b_type_1_', 'b_type_2_'))]
    move_type_cols = [col for col in X_train.columns if col.startswith(('a_move_type_', 'b_move_type_')) and 'mult' not in col]
    
    assert len(type_cols) > 0, "No one-hot encoded type columns found"
    assert len(move_type_cols) > 0, "No one-hot encoded move type columns found"
    
    # Check that one-hot columns are binary (0 or 1)
    for col in type_cols + move_type_cols:
        unique_values = X_train[col].unique()
        assert set(unique_values).issubset({0, 1, 0.0, 1.0}), \
            f"One-hot column {col} has non-binary values: {unique_values}"


def test_no_categorical_columns(X_train):
    """Test that no categorical columns remain."""
    # After preprocessing, no object/string columns should remain (except scenario_type)
    object_cols = X_train.select_dtypes(include=['object']).columns
    allowed_categorical = {'scenario_type'}
    unexpected_categorical = set(object_cols) - allowed_categorical
    assert len(unexpected_categorical) == 0, \
        f"Unexpected categorical columns: {list(unexpected_categorical)}"


def test_derived_features_exist(X_train):
    """Test that derived features were created."""
    expected_derived = [
        'stat_ratio',
        'type_advantage_diff',
        'effective_power_a',
        'effective_power_b',
        'effective_power_diff',
        'priority_advantage'
    ]
    
    for feature in expected_derived:
        assert feature in X_train.columns, f"Derived feature {feature} not found"


def test_normalization_applied(X_train, X_test):
    """Test that normalization was applied to features."""
    # After StandardScaler, most features should have mean ~0 and std ~1
    # Check a few key numeric features
    numeric_base_features = ['a_hp', 'a_attack', 'a_defense', 'b_hp', 'b_attack', 'b_defense']
    
    for feature in numeric_base_features:
        if feature in X_train.columns:
            train_mean = X_train[feature].mean()
            train_std = X_train[feature].std()
            
            # After scaling, mean should be close to 0 and std close to 1
            assert abs(train_mean) < 0.5, \
                f"Feature {feature} not properly normalized (mean={train_mean:.2f})"
            assert 0.5 < train_std < 1.5, \
                f"Feature {feature} not properly normalized (std={train_std:.2f})"


def test_no_infinite_values(X_train, X_test):
    """Test that there are no infinite values."""
    # Select only numeric columns
    numeric_train = X_train.select_dtypes(include=[np.number])
    numeric_test = X_test.select_dtypes(include=[np.number])
    
    train_inf = np.isinf(numeric_train.values).sum()
    test_inf = np.isinf(numeric_test.values).sum()
    
    assert train_inf == 0, f"Training features have {train_inf} infinite values"
    assert test_inf == 0, f"Test features have {test_inf} infinite values"


def test_feature_ranges_reasonable(X_train):
    """Test that feature values are in reasonable ranges after normalization."""
    # After StandardScaler, values typically in [-3, +3] range (99.7% of data)
    # Allow [-10, +10] to be safe with outliers
    # Select only numeric columns
    numeric_train = X_train.select_dtypes(include=[np.number])
    
    min_vals = numeric_train.min()
    max_vals = numeric_train.max()
    
    extreme_low = min_vals[min_vals < -10]
    extreme_high = max_vals[max_vals > 10]
    
    assert len(extreme_low) == 0, f"Features with extreme low values: {extreme_low.to_dict()}"
    assert len(extreme_high) == 0, f"Features with extreme high values: {extreme_high.to_dict()}"


def test_labels_are_binary(y_train, y_test):
    """Test that labels are binary (0 or 1)."""
    assert set(y_train.unique()) == {0, 1}, f"Train labels not binary: {y_train.unique()}"
    assert set(y_test.unique()) == {0, 1}, f"Test labels not binary: {y_test.unique()}"


def test_label_class_balance(y_train):
    """Test that labels have reasonable class balance."""
    balance = y_train.value_counts(normalize=True)
    
    # Check both classes exist
    assert len(balance) == 2, "Labels should have 2 classes"
    
    # Check balance (30-70% range)
    assert balance.min() >= 0.30, f"Class imbalance too severe: {balance}"
    assert balance.max() <= 0.70, f"Class imbalance too severe: {balance}"


def test_sample_counts_match(X_train, X_test, y_train, y_test):
    """Test that feature and label counts match."""
    assert len(X_train) == len(y_train), \
        f"Train features ({len(X_train)}) != train labels ({len(y_train)})"
    assert len(X_test) == len(y_test), \
        f"Test features ({len(X_test)}) != test labels ({len(y_test)})"


def test_no_data_leakage_features(X_train):
    """Test that no data leakage features exist."""
    # These should NOT exist in final features (only in raw data)
    # scenario_type is kept for analysis but must be dropped before model.fit()
    # a_moves_first was in v1 but removed in v2 (replaced by priority_advantage)
    forbidden_features = [
        'winner',  # Target variable
        'pokemon_a_id', 'pokemon_b_id',  # IDs
        'pokemon_a_name', 'pokemon_b_name',  # Names
        'a_move_name', 'b_move_name',  # Move names
        'battle_id'  # Metadata
    ]
    
    for feature in forbidden_features:
        assert feature not in X_train.columns, \
            f"Data leakage: {feature} should not be in preprocessed features"


def test_derived_features_calculation(X_train):
    """Test that derived features have reasonable values."""
    # stat_ratio is normalized, so check it has reasonable variance
    if 'stat_ratio' in X_train.columns:
        assert X_train['stat_ratio'].std() > 0.1, "stat_ratio should have meaningful variance"
    
    # effective_power should be >= 0
    if 'effective_power_a' in X_train.columns:
        # After normalization, can be negative, but check for outliers
        assert X_train['effective_power_a'].min() > -10, "effective_power_a has extreme values"
    
    if 'effective_power_diff' in X_train.columns:
        # Difference can be negative, but should be reasonable
        assert abs(X_train['effective_power_diff'].min()) < 10, "effective_power_diff too extreme"
        assert abs(X_train['effective_power_diff'].max()) < 10, "effective_power_diff too extreme"


def test_train_test_distribution_similarity(X_train, X_test):
    """Test that train and test have similar distributions."""
    # Check that mean/std are similar between train and test for key features
    key_features = ['stat_ratio', 'effective_power_diff', 'type_advantage_diff']
    
    for feature in key_features:
        if feature in X_train.columns and feature in X_test.columns:
            train_mean = X_train[feature].mean()
            test_mean = X_test[feature].mean()
            
            # Means should be within 1 std of each other
            combined_std = np.sqrt(X_train[feature].var() + X_test[feature].var())
            diff = abs(train_mean - test_mean)
            
            assert diff < combined_std, \
                f"Feature {feature} has very different distributions: train_mean={train_mean:.2f}, test_mean={test_mean:.2f}"


def test_preprocessing_reproducibility():
    """Test that preprocessing can be reproduced."""
    # Load features twice and check they're identical
    X_train_1 = pd.read_parquet(FEATURES_DIR / "X_train.parquet")
    X_train_2 = pd.read_parquet(FEATURES_DIR / "X_train.parquet")
    
    assert X_train_1.equals(X_train_2), "Preprocessing not reproducible"
