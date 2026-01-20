# app/api/services/move_service.py

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.models import Move


# -------------------------
# 🔹 Liste des capacités
# -------------------------

def list_moves(db: Session) -> List[Move]:
    """
    Retourne toutes les capacités (SQLAlchemy)
    """
    return (
        db.query(Move)
        .options(joinedload(Move.type))
        .all()
    )


# -------------------------
# 🔹 Détail capacité
# -------------------------

def get_move_by_id(db: Session, move_id: int) -> Optional[Move]:
    """
    Retourne une capacité par ID (SQLAlchemy)
    """
    return (
        db.query(Move)
        .options(joinedload(Move.type))
        .filter(Move.id == move_id)
        .one_or_none()
    )
