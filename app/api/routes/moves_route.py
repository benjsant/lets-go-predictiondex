# app/api/routes/moves_route.py

from fastapi import APIRouter, HTTPException
from typing import List

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
# 🔹 Liste des capacités
# -------------------------
@router.get("/", response_model=List[MoveListItem])
def get_moves():
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
# 🔹 Détail capacité
# -------------------------
@router.get("/{move_id}", response_model=MoveDetail)
def get_move(move_id: int):
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
