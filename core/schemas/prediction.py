# core/schemas/prediction.py

"""
Prediction Schemas
==================

Pydantic models for ML prediction API requests and responses.

Used by: api_pokemon/routes/prediction_route.py
Validates: Battle prediction inputs/outputs, move scores, ML model responses
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class PredictBestMoveRequest(BaseModel):
    """
    Request for ML prediction of best move.

    Validates that Pokemon IDs are positive integers and available moves list
    contains between 1 and 20 move names.
    """

    pokemon_a_id: int = Field(
        ...,
        gt=0,
        description="ID of the user's Pokemon (attacker)"
    )
    pokemon_b_id: int = Field(
        ...,
        gt=0,
        description="ID of the opponent's Pokemon (defender)"
    )
    available_moves: List[str] = Field(
        ...,
        min_items=1,
        max_items=20,
        description="List of move names available to Pokemon A for prediction"
    )
    available_moves_b: Optional[List[str]] = Field(
        None,
        min_items=1,
        max_items=20,
        description="Optional list of move names available to Pokemon B. If provided, B will use these moves. If None, B will use its best offensive move."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "pokemon_a_id": 25,
                "pokemon_b_id": 6,
                "available_moves": ["Tonnerre", "Vive-Attaque", "Charge", "Fatal-Foudre"],
                "available_moves_b": ["Surf", "Hydrocanon"]
            }
        }


class MoveScore(BaseModel):
    """
    Individual move with its prediction score and battle outcome.

    Contains move details (name, type, power), calculated effectiveness
    (STAB, type multiplier, effective power), ML prediction (win probability,
    predicted winner), and ranking score.
    """

    move_name: str = Field(..., description="Name of the move")
    move_type: str = Field(..., description="Type of the move (e.g., 'électrik')")
    move_power: int = Field(..., ge=0, description="Base power of the move")
    effective_power: float = Field(
        ...,
        ge=0,
        description="Effective power = base_power × STAB × type_multiplier"
    )
    type_multiplier: float = Field(
        ...,
        ge=0,
        le=4,
        description="Type effectiveness multiplier (0, 0.25, 0.5, 1, 2, or 4)"
    )
    stab: float = Field(
        ...,
        description="Same Type Attack Bonus (1.0 = no bonus, 1.5 = STAB)"
    )
    priority: int = Field(
        ...,
        ge=-7,
        le=5,
        description="Move priority (-7 to 5, higher goes first)"
    )
    score: float = Field(
        ...,
        description="Composite ranking score for move selection"
    )
    win_probability: float = Field(
        ...,
        ge=0,
        le=1,
        description="ML-predicted probability that Pokemon A wins with this move"
    )
    predicted_winner: str = Field(
        ...,
        pattern="^[AB]$",
        description="Predicted winner: 'A' (user's Pokemon) or 'B' (opponent)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "move_name": "Tonnerre",
                "move_type": "électrik",
                "move_power": 90,
                "effective_power": 270.0,
                "type_multiplier": 2.0,
                "stab": 1.5,
                "priority": 0,
                "score": 270.0,
                "win_probability": 0.87,
                "predicted_winner": "A"
            }
        }


class PredictBestMoveResponse(BaseModel):
    """
    Response with best move recommendation and ranked list of all moves.

    Returns the recommended move (highest win probability), overall win
    probability, and detailed scores for all available moves sorted by
    effectiveness.
    """

    pokemon_a_id: int = Field(..., description="ID of user's Pokemon")
    pokemon_a_name: str = Field(..., description="Name of user's Pokemon")
    pokemon_b_id: int = Field(..., description="ID of opponent's Pokemon")
    pokemon_b_name: str = Field(..., description="Name of opponent's Pokemon")
    recommended_move: str = Field(
        ...,
        description="Move with highest predicted win probability"
    )
    win_probability: float = Field(
        ...,
        ge=0,
        le=1,
        description="Win probability with the recommended move"
    )
    all_moves: List[MoveScore] = Field(
        ...,
        description="All moves ranked by effectiveness (descending order)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "pokemon_a_id": 25,
                "pokemon_a_name": "Pikachu",
                "pokemon_b_id": 6,
                "pokemon_b_name": "Dracaufeu",
                "recommended_move": "Tonnerre",
                "win_probability": 0.87,
                "all_moves": [
                    {
                        "move_name": "Tonnerre",
                        "move_type": "électrik",
                        "move_power": 90,
                        "effective_power": 270.0,
                        "type_multiplier": 2.0,
                        "stab": 1.5,
                        "priority": 0,
                        "score": 270.0,
                        "win_probability": 0.87,
                        "predicted_winner": "A"
                    },
                    {
                        "move_name": "Vive-Attaque",
                        "move_type": "normal",
                        "move_power": 40,
                        "effective_power": 40.0,
                        "type_multiplier": 1.0,
                        "stab": 1.0,
                        "priority": 1,
                        "score": 40.0,
                        "win_probability": 0.62,
                        "predicted_winner": "A"
                    }
                ]
            }
        }
