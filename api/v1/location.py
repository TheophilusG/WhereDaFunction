from datetime import datetime
from typing import Dict

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from core.database import get_db
from core.deps import get_current_user
from schema.location import LocationUpdate
from services import friend_service, location_service


router = APIRouter(tags=["location"])


class ConnectionManager:
    def __init__(self) -> None:
        self.connections: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections[user_id] = websocket

    def disconnect(self, user_id: str) -> None:
        self.connections.pop(user_id, None)

    async def send_to_user(self, user_id: str, payload: dict) -> None:
        websocket = self.connections.get(user_id)
        if websocket:
            await websocket.send_json(payload)


manager = ConnectionManager()


@router.websocket("/ws/location")
async def websocket_location(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return

    try:
        user = location_service.user_from_access_token(token)
    except ValueError:
        await websocket.close(code=1008)
        return

    await manager.connect(user.id, websocket)

    try:
        while True:
            payload = await websocket.receive_json()
            location_payload = LocationUpdate.model_validate(payload)
            location_service.upsert_location_from_ws(
                user_id=user.id,
                latitude=location_payload.latitude,
                longitude=location_payload.longitude,
                accuracy=location_payload.accuracy,
            )

            friend_ids = location_service.get_friend_ids(user.id)
            for friend_id in friend_ids:
                await manager.send_to_user(
                    friend_id,
                    {
                        "user_id": user.id,
                        "latitude": location_payload.latitude,
                        "longitude": location_payload.longitude,
                        "accuracy": location_payload.accuracy,
                        "updated_at": datetime.utcnow().isoformat(),
                    },
                )
    except WebSocketDisconnect:
        manager.disconnect(user.id)


@router.get("/location/friends")
def list_friend_locations(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    friend_ids = [friend.id for friend in friend_service.list_friends(db, current_user.id)]
    locations = location_service.list_locations_for_users(db, friend_ids)
    return {"data": locations, "error": None, "meta": {"count": len(locations)}}


@router.post("/location/update")
async def update_location(
    payload: LocationUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    location = location_service.upsert_location(
        db,
        user_id=current_user.id,
        latitude=payload.latitude,
        longitude=payload.longitude,
        accuracy=payload.accuracy,
    )

    friend_ids = [friend.id for friend in friend_service.list_friends(db, current_user.id)]
    broadcast_payload = {
        "user_id": current_user.id,
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "accuracy": location["accuracy"],
        "updated_at": location["updated_at"].isoformat(),
    }
    for friend_id in friend_ids:
        await manager.send_to_user(friend_id, broadcast_payload)

    return {"data": location, "error": None, "meta": None}
