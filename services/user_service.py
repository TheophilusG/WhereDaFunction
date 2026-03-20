from sqlalchemy import select
from sqlalchemy.orm import Session

from core.security import get_password_hash, verify_password
from models.user import User
from schema.user import UserCreate, UserUpdate


def get_user_by_id(db: Session, user_id: str) -> User | None:
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).where(User.username == username))


def create_user(db: Session, payload: UserCreate) -> User:
    if get_user_by_email(db, payload.email):
        raise ValueError("Email already registered")
    if get_user_by_username(db, payload.username):
        raise ValueError("Username already taken")

    user = User(
        username=payload.username,
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
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
    user = get_user_by_email(db, email)
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
