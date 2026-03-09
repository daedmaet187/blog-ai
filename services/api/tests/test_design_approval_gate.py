from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth import hash_password
from app.db import Base
from app.models import Project, ProjectDesignBrief, User
from app.project_state import ProjectState
from app.routers.admin import (
    approve_project_design,
    generate_project_design_brief,
    reject_project_design,
    submit_project_design_for_approval,
)


def _make_db_session(tmp_path: Path) -> Session:
    db_file = tmp_path / "test_design_approval_gate.db"
    engine = create_engine(
        f"sqlite:///{db_file}", connect_args={"check_same_thread": False}, future=True
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


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


def _make_project(db: Session, user_id: int, state: str) -> Project:
    project = Project(
        client_user_id=user_id,
        title="Design Gate Project",
        package="growth",
        brief_en="Build a bilingual product landing page with strong CTA hierarchy.",
        brief_ar="أنشئ صفحة هبوط ثنائية اللغة مع تسلسل واضح لدعوات الإجراء.",
        state=state,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def test_design_generated_to_awaiting_admin_to_approved(tmp_path: Path):
    db = _make_db_session(tmp_path)
    try:
        client = _make_user(db, "client@example.com", "client")
        admin = _make_user(db, "admin@example.com", "admin")
        project = _make_project(db, client.id, ProjectState.READY_FOR_DESIGN.value)

        generated = generate_project_design_brief(project_id=project.id, user=admin, db=db)
        assert generated.project_id == project.id
        assert generated.state == ProjectState.DESIGN_GENERATED.value
        assert "Project: Design Gate Project" in generated.brief_text

        db.refresh(project)
        assert project.state == ProjectState.DESIGN_GENERATED.value

        saved_brief = (
            db.query(ProjectDesignBrief)
            .filter(ProjectDesignBrief.project_id == project.id)
            .first()
        )
        assert saved_brief is not None

        submitted = submit_project_design_for_approval(project_id=project.id, user=admin, db=db)
        assert submitted.state == ProjectState.AWAITING_ADMIN_DESIGN_APPROVAL.value

        approved = approve_project_design(project_id=project.id, user=admin, db=db)
        assert approved.state == ProjectState.DESIGN_APPROVED.value

        db.refresh(project)
        assert project.state == ProjectState.DESIGN_APPROVED.value
    finally:
        db.close()


def test_admin_reject_returns_state_to_design_generated(tmp_path: Path):
    db = _make_db_session(tmp_path)
    try:
        client = _make_user(db, "client2@example.com", "client")
        admin = _make_user(db, "admin2@example.com", "owner")
        project = _make_project(db, client.id, ProjectState.READY_FOR_DESIGN.value)

        generate_project_design_brief(project_id=project.id, user=admin, db=db)
        submit_project_design_for_approval(project_id=project.id, user=admin, db=db)

        rejected = reject_project_design(project_id=project.id, user=admin, db=db)
        assert rejected.state == ProjectState.DESIGN_GENERATED.value

        db.refresh(project)
        assert project.state == ProjectState.DESIGN_GENERATED.value
    finally:
        db.close()
