from pathlib import Path

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth import create_access_token, hash_password
from app.db import Base
from app.deps import current_user
from app.models import Project, User
from app.routers.projects import create_project_request, list_my_project_requests
from app.schemas import ProjectRequestCreate


@pytest.fixture
def db_session(tmp_path: Path) -> Session:
    db_file = tmp_path / "test_request_intake.db"
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


def _make_user(db: Session, email: str) -> User:
    user = User(
        email=email,
        password_hash=hash_password("password123"),
        role="client",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_current_user_rejects_invalid_token(db_session: Session):
    with pytest.raises(HTTPException) as exc:
        current_user(token="not-a-valid-token", db=db_session)
    assert exc.value.status_code == 401


def test_authenticated_client_can_create_project_request_with_package_and_bilingual_fields(
    db_session: Session,
):
    user = _make_user(db_session, "client@example.com")
    token = create_access_token(user.email)

    authed_user = current_user(token=token, db=db_session)

    created = create_project_request(
        ProjectRequestCreate(
            title="Bilingual Clinic Landing",
            package="premium",
            brief_en="Build a bilingual page focused on booking appointments quickly.",
            brief_ar="أنشئ صفحة ثنائية اللغة تركز على حجز المواعيد بسرعة.",
        ),
        user=authed_user,
        db=db_session,
    )

    assert created.client_user_id == user.id
    assert created.package == "premium"
    assert created.brief_en.startswith("Build a bilingual")
    assert created.brief_ar.startswith("أنشئ صفحة")
    assert created.state == "submitted"

    saved = db_session.query(Project).filter(Project.id == created.id).first()
    assert saved is not None
    assert saved.package == "premium"
    assert saved.brief_en == "Build a bilingual page focused on booking appointments quickly."
    assert saved.brief_ar == "أنشئ صفحة ثنائية اللغة تركز على حجز المواعيد بسرعة."

    listed = list_my_project_requests(user=authed_user, db=db_session)
    assert len(listed) == 1
    assert listed[0].id == created.id
