from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.deps import get_current_user
from schema.user import UserRead, UserUpdate
from services import friend_service, user_service


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def get_me(current_user=Depends(get_current_user)):
    return {"data": UserRead.model_validate(current_user), "error": None, "meta": None}


@router.patch("/me")
def update_me(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        user = user_service.update_user(db, current_user, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return {"data": UserRead.model_validate(user), "error": None, "meta": None}


@router.get("/search")
def search_users(
    query: str = Query(min_length=1, max_length=100),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    users = user_service.search_users(db, query=query, limit=limit)
    data = [UserRead.model_validate(user) for user in users if user.id != current_user.id]
    return {"data": data, "error": None, "meta": {"count": len(data), "limit": limit}}


@router.get("/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"data": UserRead.model_validate(user), "error": None, "meta": None}


@router.get("/me/friends")
def list_my_friends(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    friends = friend_service.list_friends(db, current_user.id)
    return {"data": [UserRead.model_validate(friend) for friend in friends], "error": None, "meta": {"count": len(friends)}}
