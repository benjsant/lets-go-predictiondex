"""
API routes – Pokémon moves
==========================

FastAPI endpoints for moves.
"""

from typing import List
from fastapi import APIRouter, HTTPException

from app.db.session import SessionLocal
from app.schemas.move import MoveListItem, MoveDetail
from app.schemas.type import TypeOut
from app.api.services.move_service import list_moves, get_move_by_id

router = APIRouter()


# -------------------------
# 🔹 List moves
# -------------------------
@router.get("/", response_model=List[MoveListItem])
def get_moves():
    """
    List all moves with lightweight information:
    - name
    - type
    - category
    - power, accuracy
    """
    with SessionLocal() as db:
        moves = list_moves(db)

        return [
            MoveListItem(
                id=m.id,
                name=m.name,
                category=m.category.name,  # ✅ use name, not object
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
    Retrieve detailed information for a specific move.
    """
    with SessionLocal() as db:
        move = get_move_by_id(db, move_id)

        if not move:
            raise HTTPException(status_code=404, detail="Move not found")

        return MoveDetail(
            id=move.id,
            name=move.name,
            category=move.category.name,  # ✅ use name
            power=move.power,
            accuracy=move.accuracy,
            description=move.description,
            damage_type=move.damage_type,
            type=TypeOut(
                id=move.type.id,
                name=move.type.name,
            ),
        )
