"""Authentication endpoints: register, login, logout."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.database import get_db
from app.models import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger("issuetracker")

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> User:
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = User(name=payload.name, email=payload.email, hashed_password=hash_password(payload.password))
    db.add(user); db.commit(); db.refresh(user)
    logger.info("user registered: id=%s email=%s", user.id, user.email)
    return user

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
    if user is None or not verify_password(payload.password, user.hashed_password):
        logger.warning("failed login attempt for email=%s", payload.email)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    token = create_access_token(subject=user.id)
    logger.info("user logged in: id=%s", user.id)
    return TokenResponse(access_token=token)

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)) -> dict:
    logger.info("user logged out: id=%s", current_user.id)
    return {"message": "Logged out successfully"}
