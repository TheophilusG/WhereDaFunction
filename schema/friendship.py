from datetime import datetime

from pydantic import BaseModel, ConfigDict

from models.friendship import FriendshipStatus


class FriendRequestCreate(BaseModel):
    addressee_id: str


class FriendshipRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    requester_id: str
    addressee_id: str
    status: FriendshipStatus
    created_at: datetime
