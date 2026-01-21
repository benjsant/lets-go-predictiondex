# api_pokemon/routes/prediction_route.py

"""
Prediction routes
=================

REST endpoints for ML-based battle prediction.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from core.db.session import get_db
from api_pokemon.services import prediction_service


router = APIRouter(prefix="/predict", tags=["prediction"])


# -------------------------
# Request/Response Schemas
# -------------------------

class PredictBestMoveRequest(BaseModel):
    """Request body for best move prediction."""

    pokemon_a_id: int = Field(..., description="ID of the user's Pokemon")
    pokemon_b_id: int = Field(..., description="ID of the opponent's Pokemon")
    available_moves: List[str] = Field(
        ...,
        description="List of move names available to Pokemon A",
        min_items=1,
        max_items=20
    )

    class Config:
        json_schema_extra = {
            "example": {
                "pokemon_a_id": 1,
                "pokemon_b_id": 4,
                "available_moves": ["Lance-Soleil", "Charge", "Bomb-Beurk", "Tranch'Herbe"]
            }
        }


class MoveScore(BaseModel):
    """Individual move with its prediction score."""

    move_name: str
    move_type: str
    move_power: int
    effective_power: float
    type_multiplier: float
    stab: float
    priority: int
    score: float
    win_probability: float
    predicted_winner: str


class PredictBestMoveResponse(BaseModel):
    """Response with recommended move and all move scores."""

    pokemon_a_id: int
    pokemon_a_name: str
    pokemon_b_id: int
    pokemon_b_name: str
    recommended_move: str
    win_probability: float
    all_moves: List[MoveScore]

    class Config:
        json_schema_extra = {
            "example": {
                "pokemon_a_id": 1,
                "pokemon_a_name": "Bulbizarre",
                "pokemon_b_id": 4,
                "pokemon_b_name": "Salamèche",
                "recommended_move": "Bomb-Beurk",
                "win_probability": 0.85,
                "all_moves": [
                    {
                        "move_name": "Bomb-Beurk",
                        "move_type": "poison",
                        "move_power": 90,
                        "effective_power": 90.0,
                        "type_multiplier": 1.0,
                        "stab": 1.0,
                        "priority": 0,
                        "score": 90.0,
                        "win_probability": 0.85,
                        "predicted_winner": "A"
                    }
                ]
            }
        }


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
        result = prediction_service.predict_best_move(
            db=db,
            pokemon_a_id=request.pokemon_a_id,
            pokemon_b_id=request.pokemon_b_id,
            available_moves_a=request.available_moves
        )
        return result

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction error: {str(e)}"
        )


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
