"""
API routes – Pokémon moves
==========================

This module defines the FastAPI routes related to Pokémon moves (abilities).

It exposes read-only endpoints allowing clients to:
- list all available moves,
- retrieve detailed information for a specific move.

The routes rely on a service layer (`move_service`) to handle database access
and business logic, ensuring a clear separation of concerns.
"""
## pylint: disable=import-error
from typing import List
from fastapi import APIRouter, HTTPException

from app.db.session import SessionLocal
from app.schemas.move import (
    MoveListItem,
    MoveDetail,
    TypeOut,
)
from app.api.services.move_service import (
    list_moves,
    get_move_by_id,
)

router = APIRouter()


# -------------------------
# 🔹 List moves
# -------------------------
@router.get("/", response_model=List[MoveListItem])
def get_moves():
    """
    Retrieve the list of all Pokémon moves.

    Returns a lightweight representation of each move including:
    - basic stats (power, accuracy, category),
    - the associated Pokémon type.

    This endpoint is intended for:
    - listings,
    - frontend selectors,
    - exploratory or analytical use cases.
    """
    with SessionLocal() as db:
        moves = list_moves(db)

        return [
            MoveListItem(
                id=m.id,
                name=m.name,
                category=m.category,
                power=m.power,
                accuracy=m.accuracy,
                type=TypeOut(
                    id=m.type.id,
                    name=m.type.name,
                ),
            )
            for m in moves
        ]


# -------------------------
# 🔹 Move detail
# -------------------------
@router.get("/{move_id}", response_model=MoveDetail)
def get_move(move_id: int):
    """
    Retrieve detailed information about a specific Pokémon move.

    Parameters
    ----------
    move_id : int
        Unique identifier of the move.

    Returns
    -------
    MoveDetail
        A detailed representation including:
        - description,
        - damage type,
        - accuracy and power,
        - associated Pokémon type.

    Raises
    ------
    HTTPException
        404 error if the requested move does not exist.
    """
    with SessionLocal() as db:
        move = get_move_by_id(db, move_id)

        if not move:
            raise HTTPException(
                status_code=404,
                detail="Move not found",
            )

        return MoveDetail(
            id=move.id,
            name=move.name,
            category=move.category,
            power=move.power,
            accuracy=move.accuracy,
            description=move.description,
            damage_type=move.damage_type,
            type=TypeOut(
                id=move.type.id,
                name=move.type.name,
            ),
        )
