# api_pokemon/services/prediction_service.py

"""
Prediction service layer
========================

Provides ML model inference for battle winner prediction.

This service is responsible for:
- loading the trained ML model
- preparing features from Pokemon data
- making predictions for battle outcomes
- recommending the best move against an opponent
"""

import os
import pickle
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import joblib
import pandas as pd
from sqlalchemy.orm import Session, joinedload

from core.models import (
    Move,
    Pokemon,
    PokemonMove,
    PokemonType,
    Type,
    TypeEffectiveness,
)

# MLflow Model Registry (optional)
try:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    from machine_learning.mlflow_integration import load_model_from_registry
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    load_model_from_registry = None


# Paths to model artifacts
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = PROJECT_ROOT / "models"


class PredictionModel:
    """Singleton to hold the loaded ML model."""

    _instance = None
    _model = None
    _scalers = None
    _metadata = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self):
        """
        Load model artifacts.

        Priority:
        1. Try MLflow Model Registry (Production stage)
        2. Fallback to local files (joblib compressed or pickle)

        Environment variables:
        - USE_MLFLOW_REGISTRY: Enable/disable registry loading (default: true)
        - MLFLOW_MODEL_NAME: Model name in registry (default: battle_winner_predictor)
        - MLFLOW_MODEL_STAGE: Model stage (default: Production)
        """
        if self._model is not None:
            return  # Already loaded

        use_mlflow = os.getenv('USE_MLFLOW_REGISTRY', 'true').lower() == 'true'
        model_name = os.getenv('MLFLOW_MODEL_NAME', 'battle_winner_predictor')
        model_stage = os.getenv('MLFLOW_MODEL_STAGE', 'Production')

        print("🔍 Loading ML model...")

        # Try MLflow Model Registry first
        if use_mlflow and MLFLOW_AVAILABLE:
            try:
                print(f"   Trying MLflow Model Registry ({model_name} @ {model_stage})...")

                # Load model bundle from registry
                model_bundle = load_model_from_registry(model_name, stage=model_stage)

                if model_bundle:
                    self._model = model_bundle.get('model')
                    self._scalers = model_bundle.get('scalers')
                    self._metadata = model_bundle.get('metadata')

                    if self._model:
                        print("✅ Model loaded from MLflow Registry")
                        version_info = model_bundle.get('version', 'unknown')
                        print(f"   Version: {version_info}")
                        return
                    print("⚠️  Model bundle incomplete, falling back to local files")
                else:
                    print("⚠️  No model in registry, falling back to local files")
            except Exception as e:
                print(f"⚠️  MLflow Registry error: {e}")
                print("   Falling back to local files...")
        elif use_mlflow and not MLFLOW_AVAILABLE:
            print("⚠️  MLflow not available, using local files")

        # Fallback: Load from local files
        print("   Loading from local files...")
        model_path = MODELS_DIR / "battle_winner_model_v2.pkl"
        scalers_path = MODELS_DIR / "battle_winner_scalers_v2.pkl"
        metadata_path = MODELS_DIR / "battle_winner_metadata_v2.pkl"

        if not model_path.exists():
            raise FileNotFoundError(
                f"Model file not found: {model_path}\n"
                f"Please train a model first using: python machine_learning/train_model.py"
            )

        # Try joblib first (compressed models), fallback to pickle
        try:
            self._model = joblib.load(model_path)
        except Exception:
            with open(model_path, 'rb') as f:
                self._model = pickle.load(f)

        with open(scalers_path, 'rb') as f:
            self._scalers = pickle.load(f)

        with open(metadata_path, 'rb') as f:
            self._metadata = pickle.load(f)

        print("✅ Model loaded from local files")

    @property
    def model(self):
        if self._model is None:
            self.load()
        return self._model

    @property
    def scalers(self):
        if self._scalers is None:
            self.load()
        return self._scalers

    @property
    def metadata(self):
        if self._metadata is None:
            self.load()
        return self._metadata


# Global model instance
prediction_model = PredictionModel()


def get_pokemon_with_details(db: Session, pokemon_id: int) -> Optional[Pokemon]:
    """
    Retrieve a Pokemon with all necessary relationships for prediction.

    Args:
        db: Database session
        pokemon_id: Pokemon ID

    Returns:
        Pokemon object with stats, types, and moves loaded, or None if not found
    """
    return (
        db.query(Pokemon)
        .options(
            joinedload(Pokemon.species),
            joinedload(Pokemon.stats),
            joinedload(Pokemon.types).joinedload(PokemonType.type),
            joinedload(Pokemon.moves).joinedload(PokemonMove.move),
        )
        .filter(Pokemon.id == pokemon_id)
        .first()
    )


def get_type_multiplier(
    move_type_id: int,
    defender_type_ids: List[int],
    type_effectiveness: Dict[Tuple[int, int], float]
) -> float:
    """
    Calculate type effectiveness multiplier.

    Args:
        move_type_id: Type ID of the attacking move
        defender_type_ids: List of defender type IDs (1 or 2)
        type_effectiveness: Dict mapping (attacking_type, defending_type) -> multiplier

    Returns:
        Total type multiplier (can be 0, 0.25, 0.5, 1, 2, or 4)
    """
    multiplier = 1.0
    for defender_type_id in defender_type_ids:
        multiplier *= type_effectiveness.get((move_type_id, defender_type_id), 1.0)
    return multiplier


def load_type_effectiveness(db: Session) -> Dict[Tuple[int, int], float]:
    """
    Load type effectiveness chart from database.

    Returns:
        Dict mapping (attacking_type_id, defending_type_id) -> multiplier
    """
    type_eff_records = db.query(TypeEffectiveness).all()

    type_eff = defaultdict(lambda: 1.0)
    for record in type_eff_records:
        type_eff[(record.attacking_type_id, record.defending_type_id)] = float(record.multiplier)

    return type_eff


def calculate_effective_power(move: Move) -> float:
    """
    Calculate effective power based on damage_type.

    Args:
        move: Move object

    Returns:
        Effective power value
    """
    power = move.power if move.power else 0
    damage_type = move.damage_type if move.damage_type else "offensif"

    if damage_type == "multi_coups":
        return power * 3
    elif damage_type == "double_degats":
        return power * 2
    elif damage_type == "deux_tours":
        return power / 2
    else:
        return power


def select_best_move_for_matchup(
    attacker: Pokemon,
    defender: Pokemon,
    available_moves: List[str],
    type_effectiveness: Dict[Tuple[int, int], float],
    _db: Session
) -> Optional[Dict]:
    """
    Select the best move for the attacker against the defender.

    Args:
        attacker: Attacking Pokemon
        defender: Defending Pokemon
        available_moves: List of move names available to the attacker
        type_effectiveness: Type effectiveness chart
        _db: Database session (unused, kept for API compatibility)

    Returns:
        Dict with move info and score, or None if no valid moves
    """
    # Get attacker types for STAB
    attacker_type_ids = [pt.type_id for pt in attacker.types]

    # Get defender types
    defender_type_ids = [pt.type_id for pt in defender.types]

    # Filter attacker's moves to only those available
    attacker_moves = [
        pm.move for pm in attacker.moves
        if pm.move.name in available_moves
        and pm.move.power is not None
        and pm.move.category.name in ['physique', 'spécial']
    ]

    if not attacker_moves:
        return None

    best_move = None
    best_score = -1

    for move in attacker_moves:
        # Calculate effective power
        eff_power = calculate_effective_power(move)

        # STAB bonus
        stab = 1.5 if move.type_id in attacker_type_ids else 1.0

        # Type effectiveness
        type_mult = get_type_multiplier(move.type_id, defender_type_ids, type_effectiveness)

        # Accuracy
        accuracy = move.accuracy if move.accuracy else 100

        # Priority
        priority = move.priority if move.priority else 0

        # Score = expected damage + priority bonus
        score = eff_power * stab * type_mult * (accuracy / 100) + priority * 50

        if score > best_score:
            best_score = score
            best_move = {
                'move_id': move.id,
                'move_name': move.name,
                'move_type_id': move.type_id,
                'move_power': move.power,
                'effective_power': eff_power,
                'move_accuracy': accuracy,
                'damage_type': move.damage_type,
                'priority': priority,
                'stab': stab,
                'type_multiplier': type_mult,
                'score': score,
            }

    return best_move


def prepare_features_for_prediction(
    pokemon_a: Pokemon,
    pokemon_b: Pokemon,
    move_a_info: Dict,
    move_b_info: Dict
) -> pd.DataFrame:
    """
    Prepare features for ML prediction.

    This function creates a single-row DataFrame with all 38 raw features
    that will be processed through the feature engineering pipeline.

    Args:
        pokemon_a: First Pokemon
        pokemon_b: Second Pokemon
        move_a_info: Dict with move A information
        move_b_info: Dict with move B information

    Returns:
        DataFrame with 1 row and 38 columns
    """
    # Get types as strings
    types_a = [pt.type.name for pt in pokemon_a.types]
    a_type_1 = types_a[0] if len(types_a) > 0 else 'none'
    a_type_2 = types_a[1] if len(types_a) > 1 else 'none'

    types_b = [pt.type.name for pt in pokemon_b.types]
    b_type_1 = types_b[0] if len(types_b) > 0 else 'none'
    b_type_2 = types_b[1] if len(types_b) > 1 else 'none'

    # Get move type names

    # We need to query the type names
    # For simplicity, we'll pass them from the move_info dicts
    # (They should be added by the caller)

    # Calculate total stats
    a_total_stats = (
        pokemon_a.stats.hp + pokemon_a.stats.attack + pokemon_a.stats.defense +
        pokemon_a.stats.sp_attack + pokemon_a.stats.sp_defense + pokemon_a.stats.speed
    )
    b_total_stats = (
        pokemon_b.stats.hp + pokemon_b.stats.attack + pokemon_b.stats.defense +
        pokemon_b.stats.sp_attack + pokemon_b.stats.sp_defense + pokemon_b.stats.speed
    )

    # Determine who moves first
    a_moves_first = 1 if move_a_info['priority'] > move_b_info['priority'] else (
        1 if (move_a_info['priority'] == move_b_info['priority'] and pokemon_a.stats.speed > pokemon_b.stats.speed) else 0
    )

    # Build feature dict
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
    """
    Apply the same feature engineering pipeline as training.

    Steps:
    1. One-hot encode categorical features
    2. Normalize numerical features (StandardScaler)
    3. Create derived features
    4. Normalize derived features (StandardScaler)

    Args:
        df_raw: Raw features DataFrame (1 row, 31 columns)

    Returns:
        Engineered features DataFrame (1 row, 133 columns)
    """
    model_instance = prediction_model
    scalers = model_instance.scalers
    # Utiliser 'features' au lieu de 'feature_columns' (compatibilité metadata v2)
    feature_columns = model_instance.metadata.get('feature_columns') or model_instance.metadata.get('features')

    # Step 1: One-hot encode categorical features
    categorical_features = ['a_type_1', 'a_type_2', 'b_type_1', 'b_type_2', 'a_move_type', 'b_move_type']

    X_encoded = df_raw.copy()

    for feature in categorical_features:
        if feature in X_encoded.columns:
            dummies = pd.get_dummies(X_encoded[feature], prefix=feature, drop_first=False)
            X_encoded = pd.concat([X_encoded, dummies], axis=1)

    # Drop categorical columns
    X_encoded = X_encoded.drop(columns=categorical_features)

    # Step 2: Normalize numerical features
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

    # Step 3: Create derived features (using original values)
    X_encoded['stat_ratio'] = df_raw['a_total_stats'] / (df_raw['b_total_stats'] + 1)
    X_encoded['type_advantage_diff'] = df_raw['a_move_type_mult'] - df_raw['b_move_type_mult']
    X_encoded['effective_power_a'] = df_raw['a_move_power'] * df_raw['a_move_stab'] * df_raw['a_move_type_mult']
    X_encoded['effective_power_b'] = df_raw['b_move_power'] * df_raw['b_move_stab'] * df_raw['b_move_type_mult']
    X_encoded['effective_power_diff'] = X_encoded['effective_power_a'] - X_encoded['effective_power_b']
    X_encoded['priority_advantage'] = df_raw['a_move_priority'] - df_raw['b_move_priority']

    # Step 4: Normalize derived features
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


def predict_best_move(
    db: Session,
    pokemon_a_id: int,
    pokemon_b_id: int,
    available_moves_a: List[str],
    available_moves_b: Optional[List[str]] = None
) -> Dict:
    """
    Predict the best move for Pokemon A against Pokemon B.

    Args:
        db: Database session
        pokemon_a_id: ID of the user's Pokemon
        pokemon_b_id: ID of the opponent's Pokemon
        available_moves_a: List of move names available to Pokemon A
        available_moves_b: Optional list of move names available to Pokemon B.
                          If provided, B will use these specific moves.
                          If None, B will use its best offensive move (default behavior).

    Returns:
        Dict with:
        - recommended_move: name of the best move
        - win_probability: probability of winning with this move
        - move_scores: list of all moves with their scores and win probabilities
    """
    # Load type effectiveness
    type_effectiveness = load_type_effectiveness(db)

    # Get Pokemon with details
    pokemon_a = get_pokemon_with_details(db, pokemon_a_id)
    pokemon_b = get_pokemon_with_details(db, pokemon_b_id)

    if not pokemon_a:
        raise ValueError(f"Pokemon A with ID {pokemon_a_id} not found")
    if not pokemon_b:
        raise ValueError(f"Pokemon B with ID {pokemon_b_id} not found")

    # Determine which moves B will use
    if available_moves_b is not None:
        # Use the specified moves for B
        all_moves_b = available_moves_b
    else:
        # Default behavior: get all offensive moves for B
        all_moves_b = [pm.move.name for pm in pokemon_b.moves if pm.move.power is not None]

    if not all_moves_b:
        raise ValueError("Pokemon B has no offensive moves available")

    # Try each move for A and predict win probability
    move_results = []

    for move_name in available_moves_a:
        # Select best move for A (this specific move)
        move_a_info = select_best_move_for_matchup(
            pokemon_a, pokemon_b, [move_name], type_effectiveness, db
        )

        if move_a_info is None:
            continue

        # Select best move for B against A
        move_b_info = select_best_move_for_matchup(
            pokemon_b, pokemon_a, all_moves_b, type_effectiveness, db
        )

        if move_b_info is None:
            continue

        # Add type names to move info
        move_a_type = db.query(Type).filter(Type.id == move_a_info['move_type_id']).first()
        move_b_type = db.query(Type).filter(Type.id == move_b_info['move_type_id']).first()

        move_a_info['move_type_name'] = move_a_type.name if move_a_type else 'normal'
        move_b_info['move_type_name'] = move_b_type.name if move_b_type else 'normal'

        # Prepare features
        features_raw = prepare_features_for_prediction(
            pokemon_a, pokemon_b, move_a_info, move_b_info
        )

        # Apply feature engineering
        features_final = apply_feature_engineering(features_raw)

        # Predict
        model = prediction_model.model

        # XGBoost 3.x requires validate_features=False to skip feature name validation
        # or we can set feature_names on the booster
        prediction = model.predict(features_final, validate_features=False)[0]
        probability = model.predict_proba(features_final, validate_features=False)[0]

        # probability[1] = probability that A wins (class 1)
        win_prob = probability[1]

        move_results.append({
            'move_name': move_name,
            'move_type': move_a_info['move_type_name'],
            'move_power': move_a_info['move_power'],
            'effective_power': move_a_info['effective_power'],
            'type_multiplier': move_a_info['type_multiplier'],
            'stab': move_a_info['stab'],
            'priority': move_a_info['priority'],
            'score': move_a_info['score'],
            'win_probability': float(win_prob),
            'predicted_winner': 'A' if prediction == 1 else 'B'
        })

    if not move_results:
        raise ValueError("No valid moves found for prediction")

    # Sort by win probability
    move_results.sort(key=lambda x: x['win_probability'], reverse=True)

    best_move = move_results[0]

    return {
        'pokemon_a_id': pokemon_a_id,
        'pokemon_a_name': pokemon_a.species.name_fr if pokemon_a.species.name_fr else pokemon_a.species.name_en,
        'pokemon_b_id': pokemon_b_id,
        'pokemon_b_name': pokemon_b.species.name_fr if pokemon_b.species.name_fr else pokemon_b.species.name_en,
        'recommended_move': best_move['move_name'],
        'win_probability': best_move['win_probability'],
        'all_moves': move_results
    }
