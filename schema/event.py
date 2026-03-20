from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from models.event import EventCategory, EventCity


class EventCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    category: EventCategory
    location_name: str = Field(min_length=1, max_length=200)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    address: str = Field(min_length=1)
    city: EventCity
    starts_at: datetime
    ends_at: datetime
    is_public: bool = True
    max_capacity: int | None = Field(default=None, ge=1)
    cover_image_url: str | None = None
    ticket_url: str | None = None

    @field_validator("ends_at")
    @classmethod
    def validate_range(cls, value: datetime, values):
        starts_at = values.data.get("starts_at")
        if starts_at and value <= starts_at:
            raise ValueError("ends_at must be after starts_at")
        return value


class EventUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=1)
    category: EventCategory | None = None
    location_name: str | None = Field(default=None, min_length=1, max_length=200)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    address: str | None = Field(default=None, min_length=1)
    city: EventCity | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    is_public: bool | None = None
    is_live: bool | None = None
    max_capacity: int | None = Field(default=None, ge=1)
    cover_image_url: str | None = None
    ticket_url: str | None = None


class EventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    host_id: str
    title: str
    description: str
    category: EventCategory
    location_name: str
    latitude: float
    longitude: float
    address: str
    city: EventCity
    starts_at: datetime
    ends_at: datetime
    is_public: bool
    is_live: bool
    max_capacity: int | None
    cover_image_url: str | None
    ticket_url: str | None
    created_at: datetime
