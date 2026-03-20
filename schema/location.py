from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LocationUpdate(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    accuracy: float | None = Field(default=None, ge=0)


class LocationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    latitude: float
    longitude: float
    accuracy: float | None
    updated_at: datetime
