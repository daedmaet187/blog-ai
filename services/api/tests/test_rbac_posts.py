from pathlib import Path

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth import hash_password
from app.db import Base
from app.models import Post, User
from app.routers.posts import create_post, publish_post, update_post
from app.schemas import PostCreate, PostUpdate


@pytest.fixture
def db_session(tmp_path: Path) -> Session:
    db_file = tmp_path / "test_rbac_posts.db"
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


def _make_user(db: Session, email: str, role: str) -> User:
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


def test_admin_and_editor_can_create_edit_and_publish_posts(db_session: Session):
    admin = _make_user(db_session, "admin@example.com", "admin")
    editor = _make_user(db_session, "editor@example.com", "editor")

    admin_post = create_post(
        PostCreate(title="Admin Post", slug="admin-post", content="draft"),
        user=admin,
        db=db_session,
    )
    assert admin_post.status == "draft"

    editor_post = create_post(
        PostCreate(title="Editor Post", slug="editor-post", content="draft"),
        user=editor,
        db=db_session,
    )
    assert editor_post.status == "draft"

    updated_post = update_post(
        editor_post.id,
        PostUpdate(title="Editor Post Updated"),
        user=editor,
        db=db_session,
    )
    assert updated_post.title == "Editor Post Updated"

    publish_result = publish_post(editor_post.id, user=editor, db=db_session)
    assert publish_result.post.status == "published"


def test_reader_is_denied_create_edit_and_publish_posts(db_session: Session):
    admin = _make_user(db_session, "admin2@example.com", "admin")
    reader = _make_user(db_session, "reader@example.com", "reader")

    with pytest.raises(HTTPException) as create_error:
        create_post(
            PostCreate(title="Reader Post", slug="reader-post", content="draft"),
            user=reader,
            db=db_session,
        )
    assert create_error.value.status_code == 403

    draft_post = create_post(
        PostCreate(title="Admin Seed", slug="admin-seed", content="draft"),
        user=admin,
        db=db_session,
    )

    with pytest.raises(HTTPException) as edit_error:
        update_post(
            draft_post.id,
            PostUpdate(title="Reader Edit"),
            user=reader,
            db=db_session,
        )
    assert edit_error.value.status_code == 403

    with pytest.raises(HTTPException) as publish_error:
        publish_post(draft_post.id, user=reader, db=db_session)
    assert publish_error.value.status_code == 403

    post = db_session.query(Post).filter(Post.id == draft_post.id).first()
    assert post is not None
    assert post.status == "draft"
