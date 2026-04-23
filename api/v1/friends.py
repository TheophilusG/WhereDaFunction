from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.deps import get_current_user
from schema.friendship import FriendRequestCreate
from services import event_service, friend_service


router = APIRouter(prefix="/friends", tags=["friends"])


@router.post("/request", status_code=status.HTTP_201_CREATED)
def send_friend_request(
    payload: FriendRequestCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        friendship = friend_service.send_friend_request(db, requester_id=current_user.id, addressee_id=payload.addressee_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return {"data": friendship, "error": None, "meta": None}


@router.patch("/{friendship_id}/accept")
def accept_friend_request(
    friendship_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        friendship = friend_service.accept_friend_request(db, friendship_id=friendship_id, user_id=current_user.id)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return {"data": friendship, "error": None, "meta": None}


@router.delete("/{friendship_id}")
def remove_friendship(
    friendship_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    deleted = friend_service.remove_friendship(db, friendship_id=friendship_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Friendship not found")
    return {"data": {"deleted": True}, "error": None, "meta": None}


@router.get("/requests/incoming")
def list_incoming_friend_requests(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    requests = friend_service.list_incoming_friend_requests(db, user_id=current_user.id)
    return {"data": requests, "error": None, "meta": {"count": len(requests)}}


@router.get("/requests/outgoing")
def list_outgoing_friend_requests(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    requests = friend_service.list_outgoing_friend_requests(db, user_id=current_user.id)
    return {"data": requests, "error": None, "meta": {"count": len(requests)}}


@router.get("/events")
def friends_events(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    events = event_service.list_events_friends_are_attending(db, current_user.id)
    return {"data": events, "error": None, "meta": {"count": len(events)}}
