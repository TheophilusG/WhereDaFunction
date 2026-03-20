from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class EventCategory(str, Enum):
    PARTY = "party"
    BRUNCH = "brunch"
    CONCERT = "concert"
    SPORTS = "sports"
    NETWORKING = "networking"
    OTHER = "other"


class EventCity(str, Enum):
    DUBAI = "dubai"
    ABU_DHABI = "abu_dhabi"


class Event(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    host_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[EventCategory] = mapped_column(SQLEnum(EventCategory, name="event_category"), nullable=False)
    location_name: Mapped[str] = mapped_column(String(200), nullable=False)
    latitude: Mapped[float] = mapped_column(nullable=False)
    longitude: Mapped[float] = mapped_column(nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[EventCity] = mapped_column(SQLEnum(EventCity, name="event_city"), nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_live: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    max_capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cover_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    ticket_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    host = relationship("User", back_populates="events")
    rsvps = relationship("RSVP", back_populates="event", cascade="all, delete-orphan")
