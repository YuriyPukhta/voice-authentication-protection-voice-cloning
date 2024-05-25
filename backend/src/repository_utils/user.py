import guid as guid
from sqlalchemy.orm import Session

from src.models_db import RequestAuth, RequestSession, User


def get_user_by_id(id: str, db: Session):
    return db.query(User).filter(User.id == id).first()


def get_user_by_username(username: str, db: Session):
    return db.query(User).filter(User.name == username).first()


def add_user(username: str, db: Session):
    db_record = User(name=username)
    db.add(db_record)
    db.flush()
    return db_record
