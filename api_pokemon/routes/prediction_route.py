# api_pokemon/routes/prediction_route.py

"""
Prediction routes
=================

REST endpoints for ML-based battle prediction.
"""

import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api_pokemon.monitoring.drift_detection import drift_detector
from api_pokemon.monitoring.metrics import track_prediction
from api_pokemon.services import prediction_service
from core.db.session import get_db
from core.schemas.prediction import PredictBestMoveRequest, PredictBestMoveResponse

router = APIRouter(prefix="/predict", tags=["prediction"])


# -------------------------
# Routes
# -------------------------

@router.post("/best-move", response_model=PredictBestMoveResponse)
def predict_best_move(
    request: PredictBestMoveRequest,
    db: Session = Depends(get_db)
):
    """
    Predict the best move for Pokemon A against Pokemon B.

    This endpoint uses a trained XGBoost model (94.24% accuracy) to predict
    the outcome of a battle for each available move, and recommends the move
    with the highest win probability.

    **How it works:**
    1. For each available move of Pokemon A:
       - Simulates the move choice
       - Selects the best counter-move for Pokemon B
       - Calculates battle features (stats, types, STAB, effectiveness)
       - Predicts win probability using ML model
    2. Returns moves ranked by win probability

    **Use case:**
    Help children choose the best move against an opponent in Pokemon Let's Go.

    **Args:**
    - pokemon_a_id: ID of the user's Pokemon
    - pokemon_b_id: ID of the opponent's Pokemon
    - available_moves: List of move names that Pokemon A knows

    **Returns:**
    - recommended_move: The move with highest win probability
    - win_probability: Probability of winning (0-1)
    - all_moves: All moves ranked by win probability

    **Errors:**
    - 404: Pokemon not found
    - 400: Invalid move names or Pokemon has no moves
    - 500: Model inference error
    """
    try:
        start_time = time.time()

        result = prediction_service.predict_best_move(
            db=db,
            pokemon_a_id=request.pokemon_a_id,
            pokemon_b_id=request.pokemon_b_id,
            available_moves_a=request.available_moves,
            available_moves_b=request.available_moves_b
        )

        # Track prediction metrics
        prediction_duration = time.time() - start_time
        track_prediction(
            model_version="v2",
            duration=prediction_duration,
            confidence=result['win_probability'],
            win_prob=result['win_probability']
        )

        # Add prediction to production data collector with full ML feature vector
        features = result.get('best_move_features', {})
        drift_detector.add_prediction(
            features=features,
            prediction=1 if result['win_probability'] > 0.5 else 0,
            probability=result['win_probability']
        )

        # Remove internal features before returning to user
        result.pop('best_move_features', None)

        return result

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction error: {str(e)}"
        ) from e


@router.get("/model-info")
def get_model_info():
    """
    Get information about the loaded ML model.

    Returns:
    - model_type: Type of ML model (XGBClassifier)
    - version: Model version
    - n_features: Number of features
    - metrics: Test set performance metrics
    - trained_at: Training timestamp
    """
    model_instance = prediction_service.prediction_model
    metadata = model_instance.metadata

    return {
        "model_type": metadata['model_type'],
        "version": metadata['version'],
        "n_features": metadata['n_features'],
        "metrics": metadata['metrics'],
        "trained_at": metadata['trained_at'],
        "hyperparameters": metadata['hyperparameters']
    }
