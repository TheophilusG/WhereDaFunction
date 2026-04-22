from sqlalchemy import select
from sqlalchemy.orm import Session

from core.security import get_password_hash, verify_password
from models.user import User
from schema.user import UserCreate, UserUpdate


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _normalize_username(username: str) -> str:
    return username.strip().lower()


def get_user_by_id(db: Session, user_id: str) -> User | None:
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).where(User.username == username))


def create_user(db: Session, payload: UserCreate) -> User:
    email = _normalize_email(payload.email)
    username = _normalize_username(payload.username)

    if get_user_by_email(db, email):
        raise ValueError("Email already registered")
    if get_user_by_username(db, username):
        raise ValueError("Username already taken")

    user = User(
        username=username,
        full_name=payload.full_name.strip(),
        email=email,
        phone=payload.phone.strip() if payload.phone else None,
        avatar_url=payload.avatar_url,
        bio=payload.bio,
        is_vendor=payload.is_vendor,
        hashed_password=get_password_hash(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    identifier = email.strip()
    user = get_user_by_email(db, _normalize_email(identifier))
    if not user:
        user = get_user_by_username(db, _normalize_username(identifier))
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def update_user(db: Session, user: User, payload: UserUpdate) -> User:
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user
