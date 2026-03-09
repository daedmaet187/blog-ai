from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth import hash_password
from app.db import Base
from app.models import AuditLog, ModerationQueueItem, User
from app.moderation.routes import list_moderation_queue, override_moderation_item
from app.routers.posts import create_post, publish_post
from app.schemas import ModerationOverrideIn, PostCreate


@pytest.fixture
def db_session(tmp_path: Path) -> Session:
    db_file = tmp_path / "test_moderation_workflow.db"
    engine = create_engine(
        f"sqlite:///{db_file}", connect_args={"check_same_thread": False}, future=True
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def _make_user(db: Session, email: str, role: str = "editor") -> User:
    user = User(
        email=email,
        password_hash=hash_password("password123"),
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_flagged_post_enters_queue_and_can_be_overridden_with_audit_log(db_session: Session):
    editor = _make_user(db_session, "editor@example.com", role="editor")
    admin = _make_user(db_session, "admin@example.com", role="admin")

    create_post(
        PostCreate(title="Seed", slug="seed", content="Same body content"),
        user=editor,
        db=db_session,
    )
    flagged_post = create_post(
        PostCreate(title="Second", slug="second", content="Same body content"),
        user=editor,
        db=db_session,
    )

    publish_post(flagged_post.id, user=editor, db=db_session)

    queue_items = list_moderation_queue(user=admin, db=db_session)
    assert len(queue_items) == 1
    assert queue_items[0].post_id == flagged_post.id
    assert queue_items[0].status == "pending"

    overridden = override_moderation_item(
        queue_items[0].id,
        ModerationOverrideIn(action="approve", note="manual review passed"),
        user=admin,
        db=db_session,
    )
    assert overridden.status == "approved"
    assert overridden.resolved_by_user_id == admin.id

    queue_row = db_session.query(ModerationQueueItem).filter(ModerationQueueItem.id == queue_items[0].id).first()
    assert queue_row is not None
    assert queue_row.status == "approved"

    audit_events = db_session.query(AuditLog).order_by(AuditLog.id.asc()).all()
    assert [event.event_type for event in audit_events] == ["moderation.flagged", "moderation.override"]
    assert audit_events[0].post_id == flagged_post.id
    assert audit_events[1].actor_user_id == admin.id
