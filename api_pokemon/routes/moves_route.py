# api_pokemon/routes/moves_route.py
"""API routes for Pokemon moves."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api_pokemon.services.move_service import (
    get_move_by_id,
    list_moves,
    list_moves_by_type,
    search_moves_by_name,
)
from core.db.session import get_db
from core.schemas.move import (
    MoveDetail,
    MoveListItem,
    MoveSelectableOut,
)
from core.schemas.type import TypeOut

router = APIRouter(prefix="/moves", tags=["Moves"])


# ============================================================
# LIST ALL MOVES
# ============================================================
@router.get("/", response_model=List[MoveListItem])
def get_moves(db: Session = Depends(get_db)):
    """List all Pokemon moves."""
    moves = list_moves(db)

    return [
        MoveListItem(
            id=move.id,
            name=move.name,
            category=move.category.name,
            power=move.power,
            accuracy=move.accuracy,
            description=move.description,
            type=TypeOut(
                id=move.type.id,
                name=move.type.name,
            ),
        )
        for move in moves
    ]


# ============================================================
# SEARCH MOVES BY NAME (FR)
# ============================================================
@router.get("/search", response_model=List[MoveListItem])
def search_moves(
    name: str = Query(
        ...,
        min_length=1,
        description="Partial or full move name (French, accent-insensitive)",
    ),
    db: Session = Depends(get_db),
):
    """Search moves by name (partial match)."""
    moves = search_moves_by_name(db, name)

    return [
        MoveListItem(
            id=move.id,
            name=move.name,
            category=move.category.name,
            power=move.power,
            accuracy=move.accuracy,
            description=move.description,
            type=TypeOut(
                id=move.type.id,
                name=move.type.name,
            ),
        )
        for move in moves
    ]


# ============================================================
# LIST MOVES BY TYPE (+ optional Pokémon filter)
# ============================================================
@router.get(
    "/by-type/{type_name}",
    response_model=List[MoveSelectableOut],
)
def get_moves_by_type(
    type_name: str,
    pokemon_id: Optional[int] = Query(
        None,
        description="Optional Pokémon ID to restrict to learnable moves",
    ),
    db: Session = Depends(get_db),
):
    """List all moves of a specific type."""
    items = list_moves_by_type(
        db=db,
        type_name=type_name,
        pokemon_id=pokemon_id,
    )

    return [
        MoveSelectableOut(
            id=item["move"].id,
            name=item["move"].name,
            category=item["move"].category.name,
            power=item["move"].power,
            accuracy=item["move"].accuracy,
            description=item["move"].description,
            type=TypeOut(
                id=item["move"].type.id,
                name=item["move"].type.name,
            ),
            learn_method=item.get("learn_method"),
            learn_level=item.get("learn_level"),
        )
        for item in items
    ]


# ============================================================
# MOVE DETAIL (ID – NON AMBIGUOUS)
# ============================================================
@router.get("/id/{move_id}", response_model=MoveDetail)
def get_move(
    move_id: int,
    db: Session = Depends(get_db),
):
    """Get move details by ID."""
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
        type=TypeOut(
            id=move.type.id,
            name=move.type.name,
        ),
    )
