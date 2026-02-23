# Smart Travel Companion Finder – Backend

## Project Overview

Smart Travel Companion Finder is a compatibility-based travel companion matching system designed for solo travelers. The backend implements a rule-based and explainable matching engine that computes compatibility scores based on structured travel preferences and trip details.

This backend provides secure authentication, compatibility scoring, match management, and controlled chat functionality using a RESTful API architecture.

## Tech Stack

- FastAPI – REST API framework
- SQLAlchemy – ORM for database interaction
- SQLite – Development database
- JWT (JSON Web Token) – Authentication
- Argon2 / Passlib – Password hashing
- Pydantic – Data validation
- Uvicorn – ASGI server

## Core Features

### User Authentication
- User Registration
- Secure Password Hashing
- JWT Token Generation
- Protected Routes

### Compatibility Matching Engine

The system computes compatibility scores using weighted parameters:

- Destination Match (25%)
- Date Overlap (20%)
- Budget Similarity (20%)
- Interest Similarity using Jaccard Index (25%)
- Travel Style Match (10%)

Scores are normalized and returned as a percentage (0–100%).

### Match Management
- Accept companion
- Store match history
- Match status tracking

### Private Chat System
- Enabled only after match acceptance
- Stores sender, receiver, and timestamp
- Restricted communication between matched users only

## Database Models

### 1. User
- user_id
- name
- email
- hashed_password
- destination
- start_date
- end_date
- budget_range
- interests
- travel_style
- discoverable

### 2. Match
- user1_id
- user2_id
- compatibility_score
- status

### 3. Message
- sender_id
- receiver_id
- content
- timestamp

## API Endpoints

### Authentication
- POST /register
- POST /login

### Matching
- POST /recommend
- POST /matches/accept

### Chat
- POST /chat/send
- GET /chat/conversations
- GET /chat/{user_id}

## Run Locally

### 1. Install Dependencies

pip install -r requirements.txt

### 2️. Run Server

uvicorn backend.app:app --reload

### 3️. Open Swagger UI

http://127.0.0.1:8000/docs

## Dataset

The system uses a synthetic dataset generated to simulate real-world solo traveler behavior. The dataset includes:

- User profile details
- Travel preferences
- Trip information
- Matching metrics

## Security Measures

- Password hashing using Argon2
- JWT-based authentication
- Protected API routes
- Environment variable configuration
- No hardcoded secrets

Batch 8 – Smart Travel Companion Finder
