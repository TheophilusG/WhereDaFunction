from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class RSVPStatus(str, Enum):
    GOING = "going"
    INTERESTED = "interested"
    NOT_GOING = "not_going"


class RSVP(Base):
    __tablename__ = "rsvps"
    __table_args__ = (UniqueConstraint("event_id", "user_id", name="uq_rsvp_event_user"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    event_id: Mapped[str] = mapped_column(String(36), ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[RSVPStatus] = mapped_column(SQLEnum(RSVPStatus, name="rsvp_status"), nullable=False)
    invited_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    event = relationship("Event", back_populates="rsvps")
    user = relationship("User", back_populates="rsvps", foreign_keys=[user_id])
