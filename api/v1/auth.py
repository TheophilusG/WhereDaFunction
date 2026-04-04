from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import create_access_token, create_refresh_token, decode_token
from schema.auth import TokenPair, TokenRefreshRequest, TokenRevokeRequest
from schema.user import UserCreate, UserLogin, UserRead
from services import token_service, user_service


router = APIRouter(prefix="/auth", tags=["auth"])


def _token_expiry_from_jwt(token: str) -> datetime:
    payload = decode_token(token)
    exp = payload.get("exp")
    if not isinstance(exp, int):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token expiry")
    return datetime.fromtimestamp(exp, tz=timezone.utc)


def _issue_token_pair(db: Session, *, user_id: str) -> TokenPair:
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)
    token_service.create_refresh_token_record(
        db,
        user_id=user_id,
        raw_token=refresh_token,
        expires_at=_token_expiry_from_jwt(refresh_token),
    )
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


@router.post("/register")
def register(payload: UserCreate, db: Session = Depends(get_db)):
    try:
        user = user_service.create_user(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    tokens = _issue_token_pair(db, user_id=user.id)

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

    tokens = _issue_token_pair(db, user_id=user.id)

    return {
        "data": {
            "user": UserRead.model_validate(user),
            "tokens": tokens,
        },
        "error": None,
        "meta": None,
    }


@router.post("/refresh")
def refresh_token(payload: TokenRefreshRequest, db: Session = Depends(get_db)):
    try:
        token_payload = decode_token(payload.refresh_token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

    if token_payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    subject = token_payload.get("sub")
    if not subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")

    existing_token = token_service.get_valid_refresh_token(db, raw_token=payload.refresh_token)
    if not existing_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is revoked or expired")
    if existing_token.user_id != subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")

    new_access_token = create_access_token(subject)
    new_refresh_token = create_refresh_token(subject)
    token_service.rotate_refresh_token(
        db,
        current_record=existing_token,
        new_raw_token=new_refresh_token,
        new_expires_at=_token_expiry_from_jwt(new_refresh_token),
    )
    tokens = TokenPair(access_token=new_access_token, refresh_token=new_refresh_token)
    return {"data": tokens, "error": None, "meta": None}


@router.post("/logout")
def logout(payload: TokenRevokeRequest, db: Session = Depends(get_db)):
    revoked = token_service.revoke_refresh_token(db, raw_token=payload.refresh_token)
    return {"data": {"revoked": revoked}, "error": None, "meta": None}


@router.post("/oauth/google")
def oauth_google():
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Google OAuth not implemented yet")


@router.post("/oauth/apple")
def oauth_apple():
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Apple OAuth not implemented yet")
