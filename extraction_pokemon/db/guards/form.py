#app\db\guards\form.py
from sqlalchemy.orm import Session
from extraction_pokemon.models import Form
from .utils import commit_if_needed

def upsert_form(session: Session, name: str, auto_commit: bool = False) -> Form:
    form = session.query(Form).filter(Form.name.ilike(name)).one_or_none()
    if form:
        return form
    form = Form(name=name)
    session.add(form)
    commit_if_needed(session, auto_commit)
    return form
