# core/models/type_effectiveness.py
"""SQLAlchemy model for type effectiveness multipliers."""

from sqlalchemy import Column, ForeignKey, Integer, Numeric

from core.db.base import Base


class TypeEffectiveness(Base):
    """
    Effectiveness of one Pokémon type against another.

    Each row indicates how much damage an attack of `attacking_type_id`
    deals to a Pokémon of `defending_type_id`.

    Business rules:
    - Multiplier = 0.0 → no effect
    - Multiplier = 0.5 → not very effective
    - Multiplier = 1.0 → normal effectiveness
    - Multiplier = 2.0 → super effective
    - Other values possible depending on game mechanics

    Use cases:
    - Battle simulation engine
    - Damage calculation
    - Feature generation for ML models predicting battle outcomes

    Example:
    ┌───────────────┬─────────────────┬─────────────┐
    │ attacking_id │ defending_id │ multiplier │
    ├───────────────┼─────────────────┼─────────────┤
    │ 5 │ 8 │ 2.0 │
    └───────────────┴─────────────────┴─────────────┘
    """

    __tablename__ = "type_effectiveness"

    #: Attacking type (FK → Type)
    attacking_type_id = Column(
        Integer,
        ForeignKey("type.id", ondelete="CASCADE"),
        primary_key=True,
    )

    #: Defending type (FK → Type)
    defending_type_id = Column(
        Integer,
        ForeignKey("type.id", ondelete="CASCADE"),
        primary_key=True,
    )

    #: Damage multiplier (e.g., 0.5, 1.0, 2.0)
    multiplier = Column(Numeric(3, 2), nullable=False)
