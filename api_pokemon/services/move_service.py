# api_pokemon/services/move_service.py
"""Database access functions for Pokemon moves."""

import unicodedata
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session, joinedload

from core.models import Move, PokemonMove, Type


# ============================================================
# Utility
# ============================================================
def normalize(text: str) -> str:
    """Normalize string for comparison (lowercase, remove accents)."""
    return "".join(
        c
        for c in unicodedata.normalize("NFD", text.lower())
        if unicodedata.category(c) != "Mn"
    )


# ============================================================
# List all moves
# ============================================================
def list_moves(db: Session) -> List[Move]:
    return (
        db.query(Move)
        .options(
            joinedload(Move.type),
            joinedload(Move.category),
        )
        .order_by(Move.id)
        .all()
    )


# ============================================================
# Get move by ID
# ============================================================
def get_move_by_id(db: Session, move_id: int) -> Optional[Move]:
    return (
        db.query(Move)
        .options(
            joinedload(Move.type),
            joinedload(Move.category),
        )
        .filter(Move.id == move_id)
        .one_or_none()
    )


# ============================================================
# Search moves by name (FR)
# ============================================================
def search_moves_by_name(db: Session, name: str) -> List[Move]:
    normalized_name = normalize(name)

    moves = (
        db.query(Move)
        .options(
            joinedload(Move.type),
            joinedload(Move.category),
        )
        .all()
    )

    return [
        move
        for move in moves
        if normalize(move.name).find(normalized_name) != -1
    ]


# ============================================================
# List moves by type (+ optional Pokémon filter)
# ============================================================
def list_moves_by_type(
    db: Session,
    type_name: str,
    pokemon_id: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Return moves for a given type with optional Pokemon learning info."""

    # Resolve type (tolerant)
    type_obj = next(
        (
            t for t in db.query(Type).all()
            if normalize(t.name).startswith(normalize(type_name))
        ),
        None,
    )

    if not type_obj:
        return []

    # --------------------------------------------------------
    # Base query (no Pokémon context)
    # --------------------------------------------------------
    if pokemon_id is None:
        moves = (
            db.query(Move)
            .options(
                joinedload(Move.type),
                joinedload(Move.category),
            )
            .filter(Move.type_id == type_obj.id)
            .order_by(Move.id)
            .all()
        )

        return [
            {
                "move": move,
                "learn_method": None,
                "learn_level": None,
            }
            for move in moves
        ]

    # --------------------------------------------------------
    # Pokémon-specific learning info
    # --------------------------------------------------------
    rows = (
        db.query(Move, PokemonMove)
        .join(PokemonMove, PokemonMove.move_id == Move.id)
        .options(
            joinedload(Move.type),
            joinedload(Move.category),
            joinedload(PokemonMove.learn_method),
        )
        .filter(
            Move.type_id == type_obj.id,
            PokemonMove.pokemon_id == pokemon_id,
        )
        .order_by(Move.id)
        .all()
    )

    return [
        {
            "move": move,
            "learn_method": pm.learn_method.name if pm.learn_method else None,
            "learn_level": pm.learn_level,
        }
        for move, pm in rows
    ]
