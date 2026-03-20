from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from models.friendship import Friendship, FriendshipStatus
from models.user import User


def send_friend_request(db: Session, *, requester_id: str, addressee_id: str) -> dict:
    if requester_id == addressee_id:
        raise ValueError("You cannot add yourself")

    pair = db.scalar(
        select(Friendship).where(
            or_(
                and_(Friendship.requester_id == requester_id, Friendship.addressee_id == addressee_id),
                and_(Friendship.requester_id == addressee_id, Friendship.addressee_id == requester_id),
            )
        )
    )
    if pair:
        raise ValueError("Friendship already exists or pending")

    friendship = Friendship(requester_id=requester_id, addressee_id=addressee_id, status=FriendshipStatus.PENDING)
    db.add(friendship)
    db.commit()
    db.refresh(friendship)
    return {
        "id": friendship.id,
        "requester_id": friendship.requester_id,
        "addressee_id": friendship.addressee_id,
        "status": friendship.status,
        "created_at": friendship.created_at,
    }


def accept_friend_request(db: Session, *, friendship_id: str, user_id: str) -> dict:
    friendship = db.get(Friendship, friendship_id)
    if not friendship:
        raise ValueError("Friend request not found")
    if friendship.addressee_id != user_id:
        raise PermissionError("Only addressee can accept this request")

    friendship.status = FriendshipStatus.ACCEPTED
    db.add(friendship)
    db.commit()
    db.refresh(friendship)

    return {
        "id": friendship.id,
        "requester_id": friendship.requester_id,
        "addressee_id": friendship.addressee_id,
        "status": friendship.status,
        "created_at": friendship.created_at,
    }


def remove_friendship(db: Session, *, friendship_id: str, user_id: str) -> bool:
    friendship = db.get(Friendship, friendship_id)
    if not friendship:
        return False

    if user_id not in {friendship.requester_id, friendship.addressee_id}:
        return False

    db.delete(friendship)
    db.commit()
    return True


def list_friends(db: Session, user_id: str) -> list[User]:
    relationships = db.scalars(
        select(Friendship).where(
            Friendship.status == FriendshipStatus.ACCEPTED,
            or_(Friendship.requester_id == user_id, Friendship.addressee_id == user_id),
        )
    ).all()

    friend_ids: set[str] = set()
    for relationship in relationships:
        if relationship.requester_id == user_id:
            friend_ids.add(relationship.addressee_id)
        else:
            friend_ids.add(relationship.requester_id)

    if not friend_ids:
        return []

    return list(db.scalars(select(User).where(User.id.in_(friend_ids))).all())
