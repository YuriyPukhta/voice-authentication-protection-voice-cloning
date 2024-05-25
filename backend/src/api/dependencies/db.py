from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models_db import Base

DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1:6666/main"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
