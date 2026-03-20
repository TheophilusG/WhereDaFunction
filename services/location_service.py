from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.database import SessionLocal
from core.security import decode_token
from models.location import UserLocation
from models.user import User
from services import friend_service


def user_from_access_token(token: str) -> User:
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise ValueError("Invalid token type")

    user_id = payload.get("sub")
    if not user_id:
        raise ValueError("Invalid token subject")

    with SessionLocal() as db:
        user = db.get(User, user_id)
        if not user:
            raise ValueError("User not found")
        db.expunge(user)
        return user


def get_friend_ids(user_id: str) -> list[str]:
    with SessionLocal() as db:
        friends = friend_service.list_friends(db, user_id)
        return [friend.id for friend in friends]


def upsert_location(
    db: Session,
    *,
    user_id: str,
    latitude: float,
    longitude: float,
    accuracy: float | None,
) -> dict:
    location = db.get(UserLocation, user_id)
    if location:
        location.latitude = latitude
        location.longitude = longitude
        location.accuracy = accuracy
        location.updated_at = datetime.utcnow()
    else:
        location = UserLocation(
            user_id=user_id,
            latitude=latitude,
            longitude=longitude,
            accuracy=accuracy,
            updated_at=datetime.utcnow(),
        )
        db.add(location)

    db.commit()
    db.refresh(location)

    return {
        "user_id": location.user_id,
        "latitude": location.latitude,
        "longitude": location.longitude,
        "accuracy": location.accuracy,
        "updated_at": location.updated_at,
    }


def upsert_location_from_ws(*, user_id: str, latitude: float, longitude: float, accuracy: float | None) -> None:
    with SessionLocal() as db:
        upsert_location(db, user_id=user_id, latitude=latitude, longitude=longitude, accuracy=accuracy)


def list_locations_for_users(db: Session, user_ids: list[str]) -> list[dict]:
    if not user_ids:
        return []

    rows = db.scalars(select(UserLocation).where(UserLocation.user_id.in_(user_ids))).all()
    return [
        {
            "user_id": row.user_id,
            "latitude": row.latitude,
            "longitude": row.longitude,
            "accuracy": row.accuracy,
            "updated_at": row.updated_at,
        }
        for row in rows
    ]
