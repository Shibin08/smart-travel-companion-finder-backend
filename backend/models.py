"""
SQLAlchemy ORM models for Smart Travel Companion Finder.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    destination = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    budget_range = Column(Float)
    interests = Column(String)
    travel_style = Column(String)
    discoverable = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    matches_as_user1 = relationship(
        "Match", foreign_keys="Match.user1_id", back_populates="user1"
    )
    matches_as_user2 = relationship(
        "Match", foreign_keys="Match.user2_id", back_populates="user2"
    )
    sent_messages = relationship(
        "Message", foreign_keys="Message.sender_id", back_populates="sender"
    )
    received_messages = relationship(
        "Message", foreign_keys="Message.receiver_id", back_populates="receiver"
    )


class Match(Base):
    __tablename__ = "matches"

    match_id = Column(Integer, primary_key=True, autoincrement=True)
    user1_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    user2_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    compatibility_score = Column(Float, nullable=False)
    status = Column(String, default="pending")  # pending / accepted / rejected
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user1 = relationship("User", foreign_keys=[user1_id], back_populates="matches_as_user1")
    user2 = relationship("User", foreign_keys=[user2_id], back_populates="matches_as_user2")


class Message(Base):
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    receiver_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    message_text = Column(String, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")
