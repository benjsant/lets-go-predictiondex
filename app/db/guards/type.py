# app/db/guards/type.py

from sqlalchemy.orm import Session
from app.models import Type
from .utils import commit_if_needed


def upsert_type(
    session: Session,
    name: str,
    auto_commit: bool = False,
) -> Type:
    type_obj = session.query(Type).filter(
        Type.name.ilike(name)
    ).one_or_none()

    if type_obj:
        return type_obj

    type_obj = Type(name=name)
    session.add(type_obj)
    commit_if_needed(session, auto_commit)
    return type_obj
