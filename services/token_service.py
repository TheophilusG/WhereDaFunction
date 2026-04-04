import hashlib
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.refresh_token import RefreshToken


def hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def create_refresh_token_record(db: Session, *, user_id: str, raw_token: str, expires_at: datetime) -> RefreshToken:
    token_record = RefreshToken(
        user_id=user_id,
        token_hash=hash_token(raw_token),
        expires_at=expires_at.replace(tzinfo=None),
    )
    db.add(token_record)
    db.commit()
    db.refresh(token_record)
    return token_record


def get_valid_refresh_token(db: Session, *, raw_token: str) -> RefreshToken | None:
    record = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == hash_token(raw_token)))
    if not record:
        return None
    if record.revoked_at is not None:
        return None
    if record.expires_at <= datetime.now(timezone.utc).replace(tzinfo=None):
        return None
    return record


def rotate_refresh_token(
    db: Session,
    *,
    current_record: RefreshToken,
    new_raw_token: str,
    new_expires_at: datetime,
) -> RefreshToken:
    new_record = RefreshToken(
        user_id=current_record.user_id,
        token_hash=hash_token(new_raw_token),
        expires_at=new_expires_at.replace(tzinfo=None),
    )
    db.add(new_record)
    db.flush()

    current_record.revoked_at = datetime.utcnow()
    current_record.replaced_by_token_id = new_record.id

    db.add(current_record)
    db.commit()
    db.refresh(new_record)
    return new_record


def revoke_refresh_token(db: Session, *, raw_token: str) -> bool:
    record = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == hash_token(raw_token)))
    if not record or record.revoked_at is not None:
        return False

    record.revoked_at = datetime.utcnow()
    db.add(record)
    db.commit()
    return True
