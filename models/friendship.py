from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class FriendshipStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    BLOCKED = "blocked"


class Friendship(Base):
    __tablename__ = "friendships"
    __table_args__ = (UniqueConstraint("requester_id", "addressee_id", name="uq_friendship_pair"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    requester_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    addressee_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[FriendshipStatus] = mapped_column(
        SQLEnum(FriendshipStatus, name="friendship_status"), nullable=False, default=FriendshipStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    requester = relationship("User", foreign_keys=[requester_id], back_populates="sent_friendships")
    addressee = relationship("User", foreign_keys=[addressee_id], back_populates="received_friendships")
