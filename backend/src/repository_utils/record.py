import guid as guid
from sqlalchemy.orm import Session

from src.models_db import Record


def get_record_by_user_id(user_id: str,  db: Session):
    return db.query(Record).filter(Record.user_id == user_id).first()

def add_record(path: str, user_id: str,  db: Session):
    db_record = Record(path=path, user_id=user_id)
    db.add(db_record)
    return db_record
