from __future__ import annotations

import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..audit import log_event
from ..deps import current_user, get_db
from ..models import ModerationQueueItem, User
from ..schemas import ModerationOverrideIn, ModerationQueueItemOut, ModerationReasonCode

router = APIRouter(prefix="/moderation", tags=["moderation"])

AUTHORING_ROLES = {"admin", "editor"}


def _ensure_editor(user: User):
    if (user.role or "").lower() not in AUTHORING_ROLES:
        raise HTTPException(status_code=403, detail="Forbidden")


def _to_out(item: ModerationQueueItem) -> ModerationQueueItemOut:
    reasons = [ModerationReasonCode(reason) for reason in json.loads(item.reasons)]
    return ModerationQueueItemOut(
        id=item.id,
        post_id=item.post_id,
        decision=item.decision,
        reasons=reasons,
        status=item.status,
        created_at=item.created_at,
        updated_at=item.updated_at,
        resolved_by_user_id=item.resolved_by_user_id,
        resolution_note=item.resolution_note,
    )


@router.get("/queue", response_model=list[ModerationQueueItemOut])
def list_moderation_queue(
    status: str = "pending",
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    if status not in {"pending", "approved", "rejected"}:
        raise HTTPException(status_code=422, detail="Invalid status")
    _ensure_editor(user)
    items = (
        db.query(ModerationQueueItem)
        .filter(ModerationQueueItem.status == status)
        .order_by(ModerationQueueItem.id.desc())
        .all()
    )
    return [_to_out(item) for item in items]


@router.post("/queue/{item_id}/override", response_model=ModerationQueueItemOut)
def override_moderation_item(
    item_id: int,
    payload: ModerationOverrideIn,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    _ensure_editor(user)

    item = db.query(ModerationQueueItem).filter(ModerationQueueItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Moderation item not found")

    item.status = "approved" if payload.action == "approve" else "rejected"
    item.resolved_by_user_id = user.id
    item.resolution_note = payload.note
    item.updated_at = datetime.utcnow()

    db.add(item)
    db.commit()
    db.refresh(item)

    log_event(
        db,
        event_type="moderation.override",
        actor_user_id=user.id,
        post_id=item.post_id,
        details=json.dumps({"item_id": item.id, "action": payload.action, "note": payload.note}),
    )

    return _to_out(item)
