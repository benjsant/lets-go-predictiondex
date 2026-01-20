#app/api/routes/type_route.py
from fastapi import APIRouter
from typing import List
from sqlalchemy.orm import Session
from app.schemas.type import TypeBase
from app.db.session import SessionLocal
from app.models import Type

router = APIRouter()

@router.get("/", response_model=List[TypeBase])
def list_types():
    with SessionLocal() as db:
        types = db.query(Type).all()
        return types
