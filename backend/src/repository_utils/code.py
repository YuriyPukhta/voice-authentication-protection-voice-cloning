import uuid

from sqlalchemy.orm import Session

from src.models_db import SixDigitCode
from src.service.generated_id import generate_random_six_digit_number


def get_code_by_code(code: int,  db: Session):
    return db.query(SixDigitCode).filter(SixDigitCode.code == code).first()


def add_code_record(user_id: uuid, db: Session):
    code = generate_random_six_digit_number()
    db_code = SixDigitCode(code=code, user_id=user_id)
    db.add(db_code)
    db.commit()
    return db_code
