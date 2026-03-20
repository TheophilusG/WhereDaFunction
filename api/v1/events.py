from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.deps import get_current_user
from models.event import EventCategory, EventCity
from models.rsvp import RSVPStatus
from schema.event import EventCreate, EventRead, EventUpdate
from services import event_service


router = APIRouter(prefix="/events", tags=["events"])


@router.get("")
def list_events(
    db: Session = Depends(get_db),
    city: EventCity | None = None,
    category: EventCategory | None = None,
    live: bool | None = None,
    starts_after: datetime | None = None,
    starts_before: datetime | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    events = event_service.list_events(
        db,
        city=city,
        category=category,
        live=live,
        starts_after=starts_after,
        starts_before=starts_before,
        limit=limit,
        offset=offset,
    )

    return {
        "data": [EventRead.model_validate(event) for event in events],
        "error": None,
        "meta": {"limit": limit, "offset": offset, "count": len(events)},
    }


@router.get("/map")
def list_events_for_map(
    db: Session = Depends(get_db),
    min_lat: float = Query(ge=-90, le=90),
    max_lat: float = Query(ge=-90, le=90),
    min_lng: float = Query(ge=-180, le=180),
    max_lng: float = Query(ge=-180, le=180),
):
    events = event_service.list_events_for_bounding_box(
        db,
        min_lat=min_lat,
        max_lat=max_lat,
        min_lng=min_lng,
        max_lng=max_lng,
    )
    return {"data": [EventRead.model_validate(event) for event in events], "error": None, "meta": {"count": len(events)}}


@router.post("", status_code=status.HTTP_201_CREATED)
def create_event(
    payload: EventCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    event = event_service.create_event(db, payload, host_id=current_user.id)
    return {"data": EventRead.model_validate(event), "error": None, "meta": None}


@router.get("/{event_id}")
def get_event(event_id: str, db: Session = Depends(get_db)):
    event = event_service.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return {"data": EventRead.model_validate(event), "error": None, "meta": None}


@router.patch("/{event_id}")
def update_event(
    event_id: str,
    payload: EventUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    event = event_service.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    if event.host_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only host can update this event")

    updated_event = event_service.update_event(db, event, payload)
    return {"data": EventRead.model_validate(updated_event), "error": None, "meta": None}


@router.delete("/{event_id}")
def delete_event(
    event_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    event = event_service.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    if event.host_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only host can delete this event")

    event_service.delete_event(db, event)
    return {"data": {"deleted": True}, "error": None, "meta": None}


@router.get("/{event_id}/attendees")
def list_attendees(event_id: str, db: Session = Depends(get_db)):
    attendees = event_service.list_event_attendees(db, event_id)
    return {"data": attendees, "error": None, "meta": {"count": len(attendees)}}


@router.post("/{event_id}/rsvp")
def upsert_rsvp(
    event_id: str,
    status_value: RSVPStatus,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        rsvp = event_service.upsert_rsvp(db, event_id=event_id, user_id=current_user.id, status=status_value)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return {"data": rsvp, "error": None, "meta": None}


@router.delete("/{event_id}/rsvp")
def remove_rsvp(
    event_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    deleted = event_service.remove_rsvp(db, event_id=event_id, user_id=current_user.id)
    return {"data": {"deleted": deleted}, "error": None, "meta": None}


@router.post("/{event_id}/invite")
def invite_friends(
    event_id: str,
    friend_ids: list[str],
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        invited_count = event_service.invite_friends(db, event_id=event_id, inviter_id=current_user.id, friend_ids=friend_ids)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return {"data": {"invited_count": invited_count}, "error": None, "meta": None}
