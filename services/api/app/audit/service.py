from __future__ import annotations

from sqlalchemy.orm import Session

from ..models import AuditLog


def log_event(db: Session, *, event_type: str, actor_user_id: int | None, post_id: int | None, details: str | None = None) -> AuditLog:
    event = AuditLog(
        event_type=event_type,
        actor_user_id=actor_user_id,
        post_id=post_id,
        details=details,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
