from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.db.session import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.auth import EmailAlreadyRegisteredError, authenticate_user, register_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, database: Annotated[Session, Depends(get_db)]) -> UserResponse:
    try:
        user = register_user(database, payload.email, payload.password)
        return UserResponse(id=user.id, email=user.email, is_active=user.is_active, onboarding_completed=False)
    except EmailAlreadyRegisteredError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered") from error


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, database: Annotated[Session, Depends(get_db)]) -> TokenResponse:
    user = authenticate_user(database, payload.email, payload.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return TokenResponse(access_token=create_access_token(user.id))
