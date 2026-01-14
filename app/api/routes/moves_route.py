"""
API routes – Pokémon moves
==========================

FastAPI endpoints for moves.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.move import MoveListItem, MoveDetail, MoveSelectableOut
from app.schemas.type import TypeOut
from app.api.services.move_service import (
    list_moves,
    get_move_by_id,
    search_moves_by_name,
    list_moves_by_type,
)

router = APIRouter(prefix="/moves", tags=["Moves"])


# -------------------------
# 🔹 List all moves
# -------------------------
@router.get("/", response_model=List[MoveListItem])
def get_moves(db: Session = Depends(get_db)):
    """
    List all moves with lightweight information:
    - name
    - type
    - category
    - power, accuracy
    """
    moves = list_moves(db)

    return [
        MoveListItem(
            id=m.id,
            name=m.name,
            category=m.category.name,
            power=m.power,
            accuracy=m.accuracy,
            type=TypeOut(id=m.type.id, name=m.type.name),
        )
        for m in moves
    ]


# -------------------------
# 🔹 Search moves by name (French)
# -------------------------
@router.get("/search", response_model=List[MoveListItem])
def search_moves(
    name: str = Query(..., min_length=1, description="Partial or full move name in French"),
    db: Session = Depends(get_db),
):
    """
    Search moves by name in French (accent- and case-insensitive).
    """
    moves = search_moves_by_name(db, name)

    if not moves:
        raise HTTPException(status_code=404, detail="No moves found matching this name")

    return [
        MoveListItem(
            id=m.id,
            name=m.name,
            category=m.category.name,
            power=m.power,
            accuracy=m.accuracy,
            type=TypeOut(id=m.type.id, name=m.type.name),
        )
        for m in moves
    ]


# -------------------------
# 🔹 Move detail
# -------------------------
@router.get("/{move_id}", response_model=MoveDetail)
def get_move(
    move_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieve detailed information for a specific move by its ID.
    """
    move = get_move_by_id(db, move_id)

    if not move:
        raise HTTPException(status_code=404, detail="Move not found")

    return MoveDetail(
        id=move.id,
        name=move.name,
        category=move.category.name,
        power=move.power,
        accuracy=move.accuracy,
        description=move.description,
        damage_type=move.damage_type,
        type=TypeOut(id=move.type.id, name=move.type.name),
    )


# -------------------------
# 🔹 List moves by type
# -------------------------
@router.get(
    "/by-type/{type_name}",
    response_model=List[MoveSelectableOut],
)
def get_moves_by_type(
    type_name: str,
    pokemon_id: Optional[int] = Query(
        None,
        description="Optional Pokémon ID to filter moves learnable by it",
    ),
    db: Session = Depends(get_db),
):
    moves = list_moves_by_type(db, type_name, pokemon_id)

    if not moves:
        raise HTTPException(status_code=404, detail="No moves found")

    results = []

    for item in moves:
        if pokemon_id:
            move, pm = item
            results.append(
                MoveSelectableOut(
                    id=move.id,
                    name=move.name,
                    category=move.category.name,
                    power=move.power,
                    accuracy=move.accuracy,
                    type=TypeOut(id=move.type.id, name=move.type.name),
                    learn_method=pm.learn_method.name if pm.learn_method else None,
                    learn_level=pm.learn_level,
                )
            )
        else:
            move = item
            results.append(
                MoveSelectableOut(
                    id=move.id,
                    name=move.name,
                    category=move.category.name,
                    power=move.power,
                    accuracy=move.accuracy,
                    type=TypeOut(id=move.type.id, name=move.type.name),
                )
            )

    return results

