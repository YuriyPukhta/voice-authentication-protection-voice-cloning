import uuid

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name: Mapped[str] = Column(String, index=True)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    record: Mapped["Record"] = relationship(back_populates="user", passive_deletes="all")
    request: Mapped["RequestSession"] = relationship(back_populates="user", passive_deletes="all")


class Record(Base):
    __tablename__ = 'record'
    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    path: Mapped[str] = Column(String, index=True)
    user_id: Mapped[uuid.UUID] = Column(
        ForeignKey("user.id", name="record_user_id_fkey", ondelete="cascade"),
        index=True,
        nullable=False,
    )
    user: Mapped["User"] = relationship(back_populates="record", passive_deletes="all")


class RequestSession(Base):
    __tablename__ = 'request_session'
    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    update_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    text: Mapped[str] = Column(String, index=True)
    user_id: Mapped[uuid.UUID] = Column(
        ForeignKey("user.id", name="request_user_id_fkey", ondelete="cascade"),
        index=True,
        nullable=False,
    )
    user: Mapped["User"] = relationship(back_populates="request", passive_deletes="all")


class RequestAuth(Base):
    __tablename__ = 'request_auth'
    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    update_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    text: Mapped[str] = Column(String, index=True)
    username: Mapped[str] = Column(String, index=True)


class SixDigitCode(Base):
    __tablename__ = 'six_digit_codes'
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(6), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id: Mapped[uuid.UUID] = Column(
        ForeignKey("user.id", name="code_user_id_fkey", ondelete="cascade"),
        index=True,
        nullable=False,
    )

