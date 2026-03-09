from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth import hash_password
from app.db import Base
from app.models import User
from app.moderation.engine import evaluate_content
from app.routers.posts import create_post, publish_post
from app.schemas import ModerationDecision, ModerationReasonCode, PostCreate


@pytest.fixture
def db_session(tmp_path: Path) -> Session:
    db_file = tmp_path / "test_moderation_engine.db"
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


def test_blocked_words_rule_flags_content():
    result = evaluate_content("This text has shit inside.", existing_contents=[])

    assert result.decision == ModerationDecision.FLAG
    assert result.reasons == [ModerationReasonCode.BLOCKED_WORD]


def test_link_spam_threshold_flags_content():
    content = "Check https://a.com https://b.com https://c.com https://d.com"

    result = evaluate_content(content, existing_contents=[])

    assert result.decision == ModerationDecision.FLAG
    assert ModerationReasonCode.TOO_MANY_LINKS in result.reasons


def test_duplicate_content_flags_content():
    existing = ["Hello   world from beta"]

    result = evaluate_content(" hello world from beta ", existing_contents=existing)

    assert result.decision == ModerationDecision.FLAG
    assert ModerationReasonCode.DUPLICATE_CONTENT in result.reasons


def test_max_media_count_flags_content():
    media = " ".join([f"![img{i}](https://cdn.example.com/{i}.png)" for i in range(5)])

    result = evaluate_content(media, existing_contents=[])

    assert result.decision == ModerationDecision.FLAG
    assert ModerationReasonCode.TOO_MANY_MEDIA in result.reasons


def test_publish_post_includes_moderation_result_from_engine(db_session: Session):
    editor = _make_user(db_session, "editor@example.com")

    create_post(
        PostCreate(title="Seed", slug="seed", content="Unique text"),
        user=editor,
        db=db_session,
    )
    to_publish = create_post(
        PostCreate(title="Publish", slug="publish", content="Unique text"),
        user=editor,
        db=db_session,
    )

    response = publish_post(to_publish.id, user=editor, db=db_session)

    assert response.post.status == "published"
    assert response.moderation.decision == ModerationDecision.FLAG
    assert response.moderation.reasons == [ModerationReasonCode.DUPLICATE_CONTENT]
