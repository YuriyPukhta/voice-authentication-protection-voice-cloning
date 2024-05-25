import guid as guid
from sqlalchemy.orm import Session

from src.models_db import RequestAuth, RequestSession


def get_request_register_by_id(id: str, db:Session):
    return db.query(RequestAuth).filter(RequestAuth.id == id).first()

def get_request_session_by_id(id: str, db:Session):
    return db.query(RequestSession).filter(RequestSession.id == id).first()

def add_request_register(text: str, username: str, db:Session):
    db_record = RequestAuth(text=text, username=username)
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def add_request_session(text: str, user_id: str, db:Session):
    db_record = RequestSession(text=text, user_id=user_id)
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def update_request_session(request_session: RequestSession, new_text: str, db:Session):
    request_session.text = new_text
    db.commit()
    db.refresh(request_session)
    return request_session
