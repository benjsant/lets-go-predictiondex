# app/db/guards/utils.py

from sqlalchemy.orm import Session


def get_one_or_none(query):
    try:
        return query.one_or_none()
    except Exception:
        return None


def commit_if_needed(session: Session, auto_commit: bool):
    if auto_commit:
        session.commit()
