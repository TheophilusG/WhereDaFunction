from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import create_access_token, create_refresh_token, decode_token
from schema.auth import TokenPair, TokenRefreshRequest
from schema.user import UserCreate, UserLogin, UserRead
from services import user_service


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(payload: UserCreate, db: Session = Depends(get_db)):
    try:
        user = user_service.create_user(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    tokens = TokenPair(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )

    return {
        "data": {
            "user": UserRead.model_validate(user),
            "tokens": tokens,
        },
        "error": None,
        "meta": None,
    }


@router.post("/login")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = user_service.authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    tokens = TokenPair(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )

    return {
        "data": {
            "user": UserRead.model_validate(user),
            "tokens": tokens,
        },
        "error": None,
        "meta": None,
    }


@router.post("/refresh")
def refresh_token(payload: TokenRefreshRequest):
    try:
        token_payload = decode_token(payload.refresh_token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

    if token_payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    subject = token_payload.get("sub")
    if not subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")

    tokens = TokenPair(
        access_token=create_access_token(subject),
        refresh_token=create_refresh_token(subject),
    )
    return {"data": tokens, "error": None, "meta": None}


@router.post("/logout")
def logout():
    return {"data": {"message": "Logged out"}, "error": None, "meta": None}


@router.post("/oauth/google")
def oauth_google():
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Google OAuth not implemented yet")


@router.post("/oauth/apple")
def oauth_apple():
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Apple OAuth not implemented yet")
