#app\db\guards\move_category.py
from sqlalchemy.orm import Session
from app.models import MoveCategory
from .utils import commit_if_needed

def upsert_move_category(session: Session, name: str, auto_commit: bool = False) -> MoveCategory:
    category = session.query(MoveCategory).filter(MoveCategory.name.ilike(name)).one_or_none()
    if category:
        return category
    category = MoveCategory(name=name)
    session.add(category)
    commit_if_needed(session, auto_commit)
    return category
