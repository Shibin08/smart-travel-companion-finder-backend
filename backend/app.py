"""
FastAPI Backend for Smart Travel Companion Finder

Endpoints:

GET  /               - Health check
POST /register       - Create a new user account
POST /login          - Authenticate and receive a JWT
POST /recommend      - Get top 5 travel companion matches (protected)
GET  /matches                      - List current user's matches (protected)
POST /matches/accept              - Create a match (pending) (protected)
PATCH /matches/{match_id}/status  - Update match status (protected)
POST /chat/send                   - Send a message (protected, requires accepted match)
GET  /chat/{id}                   - Get conversation history (protected)
"""

import os
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from auth import create_access_token, get_current_user, hash_password, verify_password
from database import Base, engine, get_db
from matching import find_matches, get_user_matches, store_match, update_match_status
from models import User
from chat import router as chat_router
from schemas import MatchListResponse, MatchResponse, MatchWithUserResponse, UserCreate, UserLogin, UserResponse

# Only auto-create tables in development mode
if os.getenv("ENV") == "development":
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart Travel Companion Finder API",
    description="Compatibility-based travel companion recommendation system",
    version="1.0.0",
)

app.include_router(chat_router)


# ----------------------------
# Response Models
# ----------------------------

class RecommendMatchItem(BaseModel):
    user_id: str
    name: str
    compatibility_score: float


class RecommendResponse(BaseModel):
    total_matches: int
    matches: List[RecommendMatchItem]


class AcceptMatchRequest(BaseModel):
    matched_user_id: str = Field(..., example="U042")
    compatibility_score: float = Field(..., example=78.5)


class UpdateMatchStatusRequest(BaseModel):
    status: str = Field(..., example="accepted", description="One of: pending, accepted, rejected, cancelled")


# ----------------------------
# Health Check
# ----------------------------

@app.get("/")
def health_check():
    return {"status": "Backend running successfully"}


# ----------------------------
# Authentication Endpoints
# ----------------------------

@app.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user account."""

    # Check duplicate email
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check duplicate user_id
    if db.query(User).filter(User.user_id == user.user_id).first():
        raise HTTPException(status_code=400, detail="User ID already taken")

    db_user = User(
        user_id=user.user_id,
        name=user.name,
        email=user.email,
        hashed_password=hash_password(user.password),  # 🔥 THIS LINE IS IMPORTANT
        destination=user.destination,
        start_date=user.start_date,
        end_date=user.end_date,
        budget_range=user.budget_range,
        interests=user.interests,
        travel_style=user.travel_style,
        discoverable=user.discoverable,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


from fastapi.security import OAuth2PasswordRequestForm

@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": user.user_id})

    return {"access_token": access_token, "token_type": "bearer"}


# ----------------------------
# Recommendation Endpoint (protected)
# ----------------------------

@app.post("/recommend", response_model=RecommendResponse)
def recommend(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the top 5 compatible travel companions (requires authentication)."""

    matches = find_matches(current_user, db)

    return {
        "total_matches": len(matches),
        "matches": matches,
    }


# ----------------------------
# List Matches Endpoint (protected)
# ----------------------------

@app.get("/matches", response_model=MatchListResponse)
def list_matches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all pending and accepted matches for the authenticated user.

    Each match includes the other user's basic info (user_id, name).
    """
    matches = get_user_matches(db, current_user.user_id)
    return {"total": len(matches), "matches": matches}


# ----------------------------
# Accept Match Endpoint (protected)
# ----------------------------

@app.post("/matches/accept", response_model=MatchResponse, status_code=201)
def accept_match(
    body: AcceptMatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a pending match between the current user and another user.

    If a match already exists between the pair, the existing match is
    returned (no duplicate is created).
    """

    if body.matched_user_id == current_user.user_id:
        raise HTTPException(status_code=400, detail="Cannot match with yourself")

    # Verify the matched user exists
    other = db.query(User).filter(User.user_id == body.matched_user_id).first()
    if not other:
        raise HTTPException(status_code=404, detail="Matched user not found")

    match, created = store_match(
        db,
        user1_id=current_user.user_id,
        user2_id=body.matched_user_id,
        compatibility_score=body.compatibility_score,
    )

    return match


# ----------------------------
# Update Match Status Endpoint (protected)
# ----------------------------

@app.patch("/matches/{match_id}/status", response_model=MatchResponse)
def change_match_status(
    match_id: int,
    body: UpdateMatchStatusRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the status of an existing match.

    Only a user who is part of the match may change its status.
    Valid statuses: pending, accepted, rejected, cancelled.
    """
    try:
        match = update_match_status(
            db,
            match_id=match_id,
            new_status=body.status,
            current_user_id=current_user.user_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return match
