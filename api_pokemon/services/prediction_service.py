# api_pokemon/services/prediction_service.py

"""
Prediction service layer
========================

Provides ML model inference for battle winner prediction.

This service is responsible for:
- making predictions for battle outcomes
- recommending the best move against an opponent
- coordinating between model loader and feature engineering

Note: Model loading and feature engineering have been refactored into
separate modules for better code organization.
"""

from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session, joinedload

from core.models import (
    Move,
    Pokemon,
    PokemonMove,
    PokemonType,
    Type,
    TypeEffectiveness,
)

# Import from refactored modules
from api_pokemon.services.model_loader import prediction_model
from api_pokemon.services.feature_engineering import (
    prepare_features_for_prediction,
    apply_feature_engineering,
)


# ================================================================
# HELPER FUNCTIONS
# ================================================================
#
# Note: Model loading is now in api_pokemon/services/model_loader.py
# Note: Feature engineering is now in api_pokemon/services/feature_engineering.py
#

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


# ================================================================
# MAIN PREDICTION FUNCTION
# ================================================================
#
# Note: prepare_features_for_prediction() and apply_feature_engineering()
#       are now in api_pokemon/services/feature_engineering.py
#

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
            'predicted_winner': 'A' if prediction == 1 else 'B',
            'features': features_final  # Store features for drift detection
        })

    if not move_results:
        raise ValueError("No valid moves found for prediction")

    # Sort by win probability
    move_results.sort(key=lambda x: x['win_probability'], reverse=True)

    best_move = move_results[0]

    # Extract features from best move for drift detection
    best_move_features = best_move.pop('features')  # Remove from move result to keep API clean

    # Convert numpy array to dict for drift detection
    # features_final is a DataFrame with 1 row, extract as dict
    import pandas as pd
    if isinstance(best_move_features, pd.DataFrame):
        features_dict = best_move_features.iloc[0].to_dict()
    else:
        features_dict = {}

    # Also remove features from all_moves to keep API response clean
    for move in move_results:
        move.pop('features', None)

    return {
        'pokemon_a_id': pokemon_a_id,
        'pokemon_a_name': pokemon_a.species.name_fr if pokemon_a.species.name_fr else pokemon_a.species.name_en,
        'pokemon_b_id': pokemon_b_id,
        'pokemon_b_name': pokemon_b.species.name_fr if pokemon_b.species.name_fr else pokemon_b.species.name_en,
        'recommended_move': best_move['move_name'],
        'win_probability': best_move['win_probability'],
        'all_moves': move_results,
        'best_move_features': features_dict  # Features for drift detection
    }
