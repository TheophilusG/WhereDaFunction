from datetime import datetime

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from models.event import Event, EventCategory, EventCity
from models.friendship import Friendship, FriendshipStatus
from models.rsvp import RSVP, RSVPStatus
from schema.event import EventCreate, EventUpdate


def create_event(db: Session, payload: EventCreate, host_id: str) -> Event:
    event = Event(host_id=host_id, **payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_event_by_id(db: Session, event_id: str) -> Event | None:
    return db.get(Event, event_id)


def list_events(
    db: Session,
    *,
    city: EventCity | None,
    category: EventCategory | None,
    live: bool | None,
    starts_after: datetime | None,
    starts_before: datetime | None,
    limit: int,
    offset: int,
) -> list[Event]:
    query = select(Event)

    if city:
        query = query.where(Event.city == city)
    if category:
        query = query.where(Event.category == category)
    if live is not None:
        query = query.where(Event.is_live == live)
    if starts_after:
        query = query.where(Event.starts_at >= starts_after)
    if starts_before:
        query = query.where(Event.starts_at <= starts_before)

    query = query.order_by(Event.starts_at.asc()).offset(offset).limit(limit)
    return list(db.scalars(query).all())


def list_events_for_bounding_box(
    db: Session,
    *,
    min_lat: float,
    max_lat: float,
    min_lng: float,
    max_lng: float,
) -> list[Event]:
    query = select(Event).where(
        and_(
            Event.latitude >= min_lat,
            Event.latitude <= max_lat,
            Event.longitude >= min_lng,
            Event.longitude <= max_lng,
        )
    )
    return list(db.scalars(query).all())


def update_event(db: Session, event: Event, payload: EventUpdate) -> Event:
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(event, field, value)

    if event.ends_at <= event.starts_at:
        raise ValueError("Event end time must be after start time")

    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def delete_event(db: Session, event: Event) -> None:
    db.delete(event)
    db.commit()


def list_event_attendees(db: Session, event_id: str) -> list[dict]:
    rows = db.scalars(select(RSVP).where(RSVP.event_id == event_id, RSVP.status == RSVPStatus.GOING)).all()
    return [
        {
            "user_id": row.user_id,
            "status": row.status,
            "created_at": row.created_at,
        }
        for row in rows
    ]


def upsert_rsvp(db: Session, *, event_id: str, user_id: str, status: RSVPStatus) -> dict:
    event = get_event_by_id(db, event_id)
    if not event:
        raise ValueError("Event not found")

    rsvp = db.scalar(select(RSVP).where(RSVP.event_id == event_id, RSVP.user_id == user_id))
    if rsvp:
        rsvp.status = status
    else:
        rsvp = RSVP(event_id=event_id, user_id=user_id, status=status)
        db.add(rsvp)

    db.commit()
    db.refresh(rsvp)
    return {
        "id": rsvp.id,
        "event_id": rsvp.event_id,
        "user_id": rsvp.user_id,
        "status": rsvp.status,
        "created_at": rsvp.created_at,
    }


def remove_rsvp(db: Session, *, event_id: str, user_id: str) -> bool:
    rsvp = db.scalar(select(RSVP).where(RSVP.event_id == event_id, RSVP.user_id == user_id))
    if not rsvp:
        return False
    db.delete(rsvp)
    db.commit()
    return True


def invite_friends(db: Session, *, event_id: str, inviter_id: str, friend_ids: list[str]) -> int:
    event = get_event_by_id(db, event_id)
    if not event:
        raise ValueError("Event not found")

    accepted_friend_rows = db.scalars(
        select(Friendship).where(
            Friendship.status == FriendshipStatus.ACCEPTED,
            or_(
                and_(Friendship.requester_id == inviter_id, Friendship.addressee_id.in_(friend_ids)),
                and_(Friendship.addressee_id == inviter_id, Friendship.requester_id.in_(friend_ids)),
            ),
        )
    ).all()

    valid_friend_ids: set[str] = set()
    for row in accepted_friend_rows:
        if row.requester_id == inviter_id:
            valid_friend_ids.add(row.addressee_id)
        else:
            valid_friend_ids.add(row.requester_id)

    invite_count = 0
    for friend_id in valid_friend_ids:
        existing = db.scalar(select(RSVP).where(RSVP.event_id == event_id, RSVP.user_id == friend_id))
        if existing:
            continue
        db.add(
            RSVP(
                event_id=event_id,
                user_id=friend_id,
                status=RSVPStatus.INTERESTED,
                invited_by=inviter_id,
            )
        )
        invite_count += 1

    db.commit()
    return invite_count


def list_events_friends_are_attending(db: Session, user_id: str) -> list[dict]:
    accepted_friendships = db.scalars(
        select(Friendship).where(
            Friendship.status == FriendshipStatus.ACCEPTED,
            or_(Friendship.requester_id == user_id, Friendship.addressee_id == user_id),
        )
    ).all()

    friend_ids: set[str] = set()
    for friendship in accepted_friendships:
        friend_ids.add(friendship.addressee_id if friendship.requester_id == user_id else friendship.requester_id)

    if not friend_ids:
        return []

    rsvps = db.scalars(
        select(RSVP).where(RSVP.user_id.in_(friend_ids), RSVP.status == RSVPStatus.GOING)
    ).all()

    if not rsvps:
        return []

    event_ids = [rsvp.event_id for rsvp in rsvps]
    events = db.scalars(select(Event).where(Event.id.in_(event_ids))).all()

    event_lookup = {event.id: event for event in events}
    return [
        {
            "friend_id": rsvp.user_id,
            "event": event_lookup.get(rsvp.event_id),
            "status": rsvp.status,
        }
        for rsvp in rsvps
        if rsvp.event_id in event_lookup
    ]
