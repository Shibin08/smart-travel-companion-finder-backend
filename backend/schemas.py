"""
Pydantic schemas for Smart Travel Companion Finder.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


# ──────────────────────────────
# User schemas
# ──────────────────────────────

class UserCreate(BaseModel):
    user_id: str
    name: str
    email: EmailStr
    password: str
    destination: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget_range: Optional[float] = None
    interests: Optional[str] = None
    travel_style: Optional[str] = None
    discoverable: bool = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    user_id: str
    name: str
    email: EmailStr
    destination: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget_range: Optional[float] = None
    interests: Optional[str] = None
    travel_style: Optional[str] = None
    discoverable: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ──────────────────────────────
# Match schemas
# ──────────────────────────────

class MatchResponse(BaseModel):
    match_id: int
    user1_id: str
    user2_id: str
    compatibility_score: float
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MatchUserInfo(BaseModel):
    """Minimal user info embedded in match responses."""
    user_id: str
    name: str


class MatchWithUserResponse(BaseModel):
    """A match record with the other user's basic info."""
    match_id: int
    compatibility_score: float
    status: str
    created_at: Optional[datetime] = None
    other_user: MatchUserInfo

    class Config:
        from_attributes = True


class MatchListResponse(BaseModel):
    """Wrapper for a list of matches."""
    total: int
    matches: list[MatchWithUserResponse]


# ──────────────────────────────
# Chat / Message schemas
# ──────────────────────────────

class ChatMessageCreate(BaseModel):
    receiver_id: str
    message_text: str


class ChatMessageResponse(BaseModel):
    message_id: int
    sender_id: str
    receiver_id: str
    message_text: str
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConversationSummary(BaseModel):
    """Summary of a conversation with another user."""
    user_id: str
    name: str
    last_message: str
    last_message_timestamp: datetime
