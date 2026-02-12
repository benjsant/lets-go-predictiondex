"""
Feature Engineering for Predictions
====================================

This module handles feature preparation and engineering for ML predictions.

Functions:
- prepare_features_for_prediction: Create raw features from Pokemon data
- apply_feature_engineering: Apply the same transformations as training
"""

from typing import Dict

import pandas as pd

from core.models import Pokemon
from api_pokemon.services.model_loader import prediction_model


def prepare_features_for_prediction(
    pokemon_a: Pokemon,
    pokemon_b: Pokemon,
    move_a_info: Dict,
    move_b_info: Dict
) -> pd.DataFrame:
    """
    Prepare raw features for ML prediction.

    This function creates a single-row DataFrame with all 38 raw features
    that will be processed through the feature engineering pipeline.

    Args:
        pokemon_a: First Pokemon with stats and types
        pokemon_b: Second Pokemon with stats and types
        move_a_info: Dictionary with move A information:
            - effective_power: float
            - move_type_name: str
            - priority: int
            - stab: float (1.5 if STAB, 1.0 otherwise)
            - type_multiplier: float
        move_b_info: Dictionary with move B information (same structure)

    Returns:
        DataFrame with 1 row and 38 columns containing raw features
    """
    # Get types as strings
    types_a = [pt.type.name for pt in pokemon_a.types]
    a_type_1 = types_a[0] if len(types_a) > 0 else 'none'
    a_type_2 = types_a[1] if len(types_a) > 1 else 'none'

    types_b = [pt.type.name for pt in pokemon_b.types]
    b_type_1 = types_b[0] if len(types_b) > 0 else 'none'
    b_type_2 = types_b[1] if len(types_b) > 1 else 'none'

    # Calculate total stats
    a_total_stats = (
        pokemon_a.stats.hp + pokemon_a.stats.attack + pokemon_a.stats.defense +
        pokemon_a.stats.sp_attack + pokemon_a.stats.sp_defense + pokemon_a.stats.speed
    )
    b_total_stats = (
        pokemon_b.stats.hp + pokemon_b.stats.attack + pokemon_b.stats.defense +
        pokemon_b.stats.sp_attack + pokemon_b.stats.sp_defense + pokemon_b.stats.speed
    )

    # Determine who moves first (priority > speed)
    a_moves_first = 1 if move_a_info['priority'] > move_b_info['priority'] else (
        1 if (move_a_info['priority'] == move_b_info['priority'] and pokemon_a.stats.speed > pokemon_b.stats.speed) else 0
    )

    # Build feature dictionary
    features = {
        # Pokemon A stats
        'a_hp': pokemon_a.stats.hp,
        'a_attack': pokemon_a.stats.attack,
        'a_defense': pokemon_a.stats.defense,
        'a_sp_attack': pokemon_a.stats.sp_attack,
        'a_sp_defense': pokemon_a.stats.sp_defense,
        'a_speed': pokemon_a.stats.speed,
        'a_type_1': a_type_1,
        'a_type_2': a_type_2,

        # Pokemon B stats
        'b_hp': pokemon_b.stats.hp,
        'b_attack': pokemon_b.stats.attack,
        'b_defense': pokemon_b.stats.defense,
        'b_sp_attack': pokemon_b.stats.sp_attack,
        'b_sp_defense': pokemon_b.stats.sp_defense,
        'b_speed': pokemon_b.stats.speed,
        'b_type_1': b_type_1,
        'b_type_2': b_type_2,

        # Move A
        'a_move_power': move_a_info['effective_power'],
        'a_move_type': move_a_info['move_type_name'],
        'a_move_priority': move_a_info['priority'],
        'a_move_stab': move_a_info['stab'],
        'a_move_type_mult': move_a_info['type_multiplier'],

        # Move B
        'b_move_power': move_b_info['effective_power'],
        'b_move_type': move_b_info['move_type_name'],
        'b_move_priority': move_b_info['priority'],
        'b_move_stab': move_b_info['stab'],
        'b_move_type_mult': move_b_info['type_multiplier'],

        # Computed features
        'speed_diff': pokemon_a.stats.speed - pokemon_b.stats.speed,
        'hp_diff': pokemon_a.stats.hp - pokemon_b.stats.hp,
        'a_total_stats': a_total_stats,
        'b_total_stats': b_total_stats,
        'a_moves_first': a_moves_first,
    }

    return pd.DataFrame([features])


def apply_feature_engineering(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Apply the same feature engineering pipeline as training."""
    model_instance = prediction_model
    scalers = model_instance.scalers

    # Get feature columns from metadata (v1 uses 'features', v2 uses 'feature_columns')
    feature_columns = model_instance.metadata.get('feature_columns') or model_instance.metadata.get('features')

    # One-hot encode categorical features
    categorical_features = ['a_type_1', 'a_type_2', 'b_type_1', 'b_type_2', 'a_move_type', 'b_move_type']

    X_encoded = df_raw.copy()

    for feature in categorical_features:
        if feature in X_encoded.columns:
            dummies = pd.get_dummies(X_encoded[feature], prefix=feature, drop_first=False)
            X_encoded = pd.concat([X_encoded, dummies], axis=1)

    X_encoded = X_encoded.drop(columns=categorical_features)

    # Normalize numerical features
    features_to_scale = [
        'a_hp', 'a_attack', 'a_defense', 'a_sp_attack', 'a_sp_defense', 'a_speed',
        'b_hp', 'b_attack', 'b_defense', 'b_sp_attack', 'b_sp_defense', 'b_speed',
        'a_move_power', 'b_move_power',
        'a_total_stats', 'b_total_stats',
        'speed_diff', 'hp_diff'
    ]
    features_to_scale = [f for f in features_to_scale if f in X_encoded.columns]

    scaler = scalers['standard_scaler']
    X_encoded[features_to_scale] = scaler.transform(X_encoded[features_to_scale])

    # Create derived features (using original values from df_raw)
    X_encoded['stat_ratio'] = df_raw['a_total_stats'] / (df_raw['b_total_stats'] + 1)
    X_encoded['type_advantage_diff'] = df_raw['a_move_type_mult'] - df_raw['b_move_type_mult']
    X_encoded['effective_power_a'] = df_raw['a_move_power'] * df_raw['a_move_stab'] * df_raw['a_move_type_mult']
    X_encoded['effective_power_b'] = df_raw['b_move_power'] * df_raw['b_move_stab'] * df_raw['b_move_type_mult']
    X_encoded['effective_power_diff'] = X_encoded['effective_power_a'] - X_encoded['effective_power_b']
    X_encoded['priority_advantage'] = df_raw['a_move_priority'] - df_raw['b_move_priority']

    # Normalize derived features
    new_features = [
        'stat_ratio', 'type_advantage_diff',
        'effective_power_a', 'effective_power_b',
        'effective_power_diff', 'priority_advantage'
    ]

    scaler_new = scalers['standard_scaler_new_features']
    X_encoded[new_features] = scaler_new.transform(X_encoded[new_features])

    # Ensure all expected features are present (add missing columns with 0)
    missing_cols = [col for col in feature_columns if col not in X_encoded.columns]
    if missing_cols:
        # Create a DataFrame with missing columns filled with 0
        missing_df = pd.DataFrame(0, index=X_encoded.index, columns=missing_cols)
        X_encoded = pd.concat([X_encoded, missing_df], axis=1)

    # Reorder columns to match training
    X_encoded = X_encoded[feature_columns]

    return X_encoded
