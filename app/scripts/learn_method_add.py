from sqlalchemy.orm import Session
from app.db.session import engine
from app.models import LearnMethod

methods = ["level_up", "ct", "move_tutor"]

with Session(engine) as session:
    for m in methods:
        exists = session.query(LearnMethod).filter_by(name=m).first()
        if not exists:
            session.add(LearnMethod(name=m))
    session.commit()
