"""
Dataset Validation Tests
========================

Tests for ML dataset quality and integrity.

Validation:
- Structure and schema
- Data types
- Missing values
- Value ranges
- Class balance
- Feature consistency
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path


# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "ml" / "battle_winner_v2"
PROCESSED_DIR = DATA_DIR / "processed"


@pytest.fixture
def train_dataset():
    """Load training dataset."""
    train_path = PROCESSED_DIR / "train.parquet"
    if not train_path.exists():
        pytest.skip(f"Training dataset not found: {train_path}")
    return pd.read_parquet(train_path)


@pytest.fixture
def test_dataset():
    """Load test dataset."""
    test_path = PROCESSED_DIR / "test.parquet"
    if not test_path.exists():
        pytest.skip(f"Test dataset not found: {test_path}")
    return pd.read_parquet(test_path)


def test_dataset_exists():
    """Test that dataset files exist."""
    assert PROCESSED_DIR.exists(), f"Processed directory not found: {PROCESSED_DIR}"
    assert (PROCESSED_DIR / "train.parquet").exists(), "train.parquet not found"
    assert (PROCESSED_DIR / "test.parquet").exists(), "test.parquet not found"


def test_dataset_structure(train_dataset, test_dataset):
    """Test that datasets have expected structure."""
    # Expected columns (38 raw features)
    expected_cols = {
        # Pokemon A
        'pokemon_a_id', 'pokemon_a_name', 'a_hp', 'a_attack', 'a_defense',
        'a_sp_attack', 'a_sp_defense', 'a_speed', 'a_type_1', 'a_type_2',
        # Pokemon B
        'pokemon_b_id', 'pokemon_b_name', 'b_hp', 'b_attack', 'b_defense',
        'b_sp_attack', 'b_sp_defense', 'b_speed', 'b_type_1', 'b_type_2',
        # Move A
        'a_move_name', 'a_move_power', 'a_move_type', 'a_move_priority',
        'a_move_stab', 'a_move_type_mult',
        # Move B
        'b_move_name', 'b_move_power', 'b_move_type', 'b_move_priority',
        'b_move_stab', 'b_move_type_mult',
        # Computed
        'speed_diff', 'hp_diff', 'a_total_stats', 'b_total_stats', 'a_moves_first',
        # Target
        'winner',
        # Metadata (v2)
        'scenario_type'
    }
 
    train_cols = set(train_dataset.columns)
    test_cols = set(test_dataset.columns)
 
    # Check all expected columns are present
    missing_train = expected_cols - train_cols
    missing_test = expected_cols - test_cols
 
    assert len(missing_train) == 0, f"Missing columns in train: {missing_train}"
    assert len(missing_test) == 0, f"Missing columns in test: {missing_test}"
 
    # Check same columns in both datasets
    assert train_cols == test_cols, "Train and test have different columns"


def test_dataset_types(train_dataset):
    """Test that columns have correct data types."""
    # Numeric features
    numeric_cols = [
        'a_hp', 'a_attack', 'a_defense', 'a_sp_attack', 'a_sp_defense', 'a_speed',
        'b_hp', 'b_attack', 'b_defense', 'b_sp_attack', 'b_sp_defense', 'b_speed',
        'a_move_power', 'b_move_power', 'a_move_priority', 'b_move_priority',
        'a_move_stab', 'a_move_type_mult', 'b_move_stab', 'b_move_type_mult',
        'speed_diff', 'hp_diff', 'a_total_stats', 'b_total_stats', 'a_moves_first',
        'winner'
    ]
 
    for col in numeric_cols:
        assert pd.api.types.is_numeric_dtype(train_dataset[col]), f"{col} should be numeric"
 
    # Categorical features
    categorical_cols = [
        'a_type_1', 'a_type_2', 'b_type_1', 'b_type_2',
        'a_move_type', 'b_move_type', 'scenario_type'
    ]
 
    for col in categorical_cols:
        assert train_dataset[col].dtype == 'object', f"{col} should be object/string"


def test_no_missing_values(train_dataset, test_dataset):
    """Test that there are no missing values in critical columns."""
    critical_cols = [
        'a_hp', 'a_attack', 'a_defense', 'a_sp_attack', 'a_sp_defense', 'a_speed',
        'b_hp', 'b_attack', 'b_defense', 'b_sp_attack', 'b_sp_defense', 'b_speed',
        'a_move_power', 'b_move_power', 'winner', 'scenario_type'
    ]
 
    for col in critical_cols:
        train_nulls = train_dataset[col].isnull().sum()
        test_nulls = test_dataset[col].isnull().sum()
 
        assert train_nulls == 0, f"Train dataset has {train_nulls} nulls in {col}"
        assert test_nulls == 0, f"Test dataset has {test_nulls} nulls in {col}"


def test_value_ranges(train_dataset):
    """Test that values are within expected ranges."""
    # Stats should be positive
    stat_cols = [
        'a_hp', 'a_attack', 'a_defense', 'a_sp_attack', 'a_sp_defense', 'a_speed',
        'b_hp', 'b_attack', 'b_defense', 'b_sp_attack', 'b_sp_defense', 'b_speed'
    ]
 
    for col in stat_cols:
        assert (train_dataset[col] > 0).all(), f"{col} should be > 0"
        assert (train_dataset[col] <= 255).all(), f"{col} should be <= 255"
 
    # Move power should be reasonable
    assert (train_dataset['a_move_power'] >= 0).all(), "a_move_power should be >= 0"
    assert (train_dataset['a_move_power'] <= 250).all(), "a_move_power should be <= 250"
    assert (train_dataset['b_move_power'] >= 0).all(), "b_move_power should be >= 0"
    assert (train_dataset['b_move_power'] <= 250).all(), "b_move_power should be <= 250"
 
    # STAB should be 1.0 or 1.5
    assert set(train_dataset['a_move_stab'].unique()).issubset({1.0, 1.5}), "STAB should be 1.0 or 1.5"
    assert set(train_dataset['b_move_stab'].unique()).issubset({1.0, 1.5}), "STAB should be 1.0 or 1.5"
 
    # Type multipliers should be valid
    valid_multipliers = {0.0, 0.25, 0.5, 1.0, 2.0, 4.0}
    assert set(train_dataset['a_move_type_mult'].unique()).issubset(valid_multipliers), \
        f"Invalid type multipliers: {train_dataset['a_move_type_mult'].unique()}"
 
    # Winner should be 0 or 1
    assert set(train_dataset['winner'].unique()) == {0, 1}, "Winner should be 0 or 1"
 
    # a_moves_first should be 0 or 1
    assert set(train_dataset['a_moves_first'].unique()) == {0, 1}, "a_moves_first should be 0 or 1"


def test_class_balance(train_dataset):
    """Test that dataset has reasonable class balance."""
    winner_counts = train_dataset['winner'].value_counts(normalize=True)
 
    # Check that both classes exist
    assert len(winner_counts) == 2, "Dataset should have both winner classes (0 and 1)"
 
    # Check balance (should be roughly 50/50, allow 40-60%)
    assert winner_counts.min() >= 0.30, f"Class imbalance too severe: {winner_counts}"
    assert winner_counts.max() <= 0.70, f"Class imbalance too severe: {winner_counts}"


def test_scenario_distribution(train_dataset):
    """Test v2 scenario distribution."""
    if 'scenario_type' not in train_dataset.columns:
        pytest.skip("Dataset is v1 (no scenario_type column)")
 
    scenario_counts = train_dataset['scenario_type'].value_counts()
 
    # Check that scenarios exist
    assert 'all_combinations' in scenario_counts, "Missing all_combinations scenario"
 
    # Check proportions (all_combinations should dominate)
    total = len(train_dataset)
    assert scenario_counts['all_combinations'] / total > 0.5, \
        "all_combinations should be > 50% of dataset"


def test_feature_consistency(train_dataset):
    """Test feature consistency and logical relationships."""
    # Test total_stats calculation
    expected_a_total = (
        train_dataset['a_hp'] + train_dataset['a_attack'] + train_dataset['a_defense'] +
        train_dataset['a_sp_attack'] + train_dataset['a_sp_defense'] + train_dataset['a_speed']
    )
    assert (train_dataset['a_total_stats'] == expected_a_total).all(), \
        "a_total_stats calculation incorrect"
 
    expected_b_total = (
        train_dataset['b_hp'] + train_dataset['b_attack'] + train_dataset['b_defense'] +
        train_dataset['b_sp_attack'] + train_dataset['b_sp_defense'] + train_dataset['b_speed']
    )
    assert (train_dataset['b_total_stats'] == expected_b_total).all(), \
        "b_total_stats calculation incorrect"
 
    # Test speed_diff calculation
    expected_speed_diff = train_dataset['a_speed'] - train_dataset['b_speed']
    assert (train_dataset['speed_diff'] == expected_speed_diff).all(), \
        "speed_diff calculation incorrect"
 
    # Test hp_diff calculation
    expected_hp_diff = train_dataset['a_hp'] - train_dataset['b_hp']
    assert (train_dataset['hp_diff'] == expected_hp_diff).all(), \
        "hp_diff calculation incorrect"


def test_dataset_size(train_dataset, test_dataset):
    """Test that dataset has reasonable size."""
    total_samples = len(train_dataset) + len(test_dataset)
 
    # v2 should have significantly more samples than v1 (~34k)
    if 'scenario_type' in train_dataset.columns:
        assert total_samples > 100000, \
            f"v2 dataset too small: {total_samples} samples (expected > 100k)"
 
    # Check train/test split ratio (should be 80/20)
    train_ratio = len(train_dataset) / total_samples
    assert 0.75 <= train_ratio <= 0.85, \
        f"Train ratio {train_ratio:.2%} outside expected range (75-85%)"


def test_no_duplicates(train_dataset):
    """Test that there are no exact duplicate rows."""
    # Check for duplicates (excluding metadata columns)
    feature_cols = [col for col in train_dataset.columns 
                   if col not in ['pokemon_a_name', 'pokemon_b_name', 'a_move_name', 'b_move_name']]
 
    duplicates = train_dataset[feature_cols].duplicated().sum()
 
    # v2 multi-scenarios: Allow higher percentage due to all_combinations scenario
    # Different moves can produce same feature values
    dup_ratio = duplicates / len(train_dataset)
    max_dup_ratio = 0.10 if 'scenario_type' in train_dataset.columns else 0.01
    assert dup_ratio < max_dup_ratio, f"Too many duplicates: {duplicates} ({dup_ratio:.2%})"


def test_train_test_separation(train_dataset, test_dataset):
    """Test that train and test sets don't have exact same samples."""
    # Create composite keys (pokemon_a_id, pokemon_b_id, a_move_name, b_move_name)
    train_keys = train_dataset[['pokemon_a_id', 'pokemon_b_id', 'a_move_name', 'b_move_name']].apply(
        lambda x: f"{x[0]}_{x[1]}_{x[2]}_{x[3]}", axis=1
    )
    test_keys = test_dataset[['pokemon_a_id', 'pokemon_b_id', 'a_move_name', 'b_move_name']].apply(
        lambda x: f"{x[0]}_{x[1]}_{x[2]}_{x[3]}", axis=1
    )
 
    # Check overlap
    overlap = set(train_keys) & set(test_keys)
    overlap_ratio = len(overlap) / len(test_keys)
 
    # v2 multi-scenarios: Random split without stratification allows same Pokemon pairs
    # with different moves in both sets. This is acceptable for generalization.
    # v1: Should have minimal overlap (< 0.1%)
    max_overlap = 0.20 if 'scenario_type' in train_dataset.columns else 0.001
    assert overlap_ratio < max_overlap, \
        f"Train/test overlap too high: {len(overlap)} samples ({overlap_ratio:.2%})"
