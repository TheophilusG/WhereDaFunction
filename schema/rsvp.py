from datetime import datetime

from pydantic import BaseModel, ConfigDict

from models.rsvp import RSVPStatus


class RSVPRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    event_id: str
    user_id: str
    status: RSVPStatus
    invited_by: str | None
    created_at: datetime
