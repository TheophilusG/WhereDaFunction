from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_vendor: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    location_sharing: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    events = relationship("Event", back_populates="host", cascade="all, delete-orphan")
    rsvps = relationship("RSVP", back_populates="user", cascade="all, delete-orphan", foreign_keys="RSVP.user_id")
    sent_friendships = relationship("Friendship", foreign_keys="Friendship.requester_id", back_populates="requester")
    received_friendships = relationship("Friendship", foreign_keys="Friendship.addressee_id", back_populates="addressee")
    location = relationship("UserLocation", back_populates="user", uselist=False, cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
