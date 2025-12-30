# app/models/type_effectiveness.py
from sqlalchemy import Column, Integer, Numeric, ForeignKey
from app.db.base import Base


class TypeEffectiveness(Base):
    __tablename__ = "type_effectiveness"

    attacking_type_id = Column(Integer, ForeignKey("type.id", ondelete="CASCADE"), primary_key=True)
    defending_type_id = Column(Integer, ForeignKey("type.id", ondelete="CASCADE"), primary_key=True)
    multiplier = Column(Numeric(3, 2), nullable=False)
