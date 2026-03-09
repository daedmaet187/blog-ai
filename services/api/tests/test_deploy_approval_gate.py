from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth import hash_password
from app.db import Base
from app.models import Project, ProjectDeployRequest, User
from app.project_state import ProjectState
from app.routers.admin import approve_project_deploy, reject_project_deploy, submit_project_deploy_for_approval


def _make_db_session(tmp_path: Path) -> Session:
    db_file = tmp_path / "test_deploy_approval_gate.db"
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
        title="Deploy Gate Project",
        package="growth",
        brief_en="Build and stage a launch-ready landing page with analytics.",
        brief_ar="أنشئ وجهّز صفحة هبوط جاهزة للإطلاق مع تحليلات أساسية.",
        state=state,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def test_deploy_submit_creates_preview_and_moves_to_awaiting_approval(tmp_path: Path):
    db = _make_db_session(tmp_path)
    try:
        client = _make_user(db, "client+deploy@example.com", "client")
        admin = _make_user(db, "admin+deploy@example.com", "admin")
        project = _make_project(db, client.id, ProjectState.BUILD_GENERATED.value)

        submitted = submit_project_deploy_for_approval(project_id=project.id, user=admin, db=db)

        assert submitted.project_id == project.id
        assert submitted.state == ProjectState.AWAITING_ADMIN_DEPLOY_APPROVAL.value
        assert submitted.deploy_status == "awaiting_admin_deploy_approval"
        assert submitted.preview_url == f"https://preview.local/projects/{project.id}"

        db.refresh(project)
        assert project.state == ProjectState.AWAITING_ADMIN_DEPLOY_APPROVAL.value

        saved_request = (
            db.query(ProjectDeployRequest)
            .filter(ProjectDeployRequest.project_id == project.id)
            .first()
        )
        assert saved_request is not None
        assert saved_request.status == "awaiting_admin_deploy_approval"
        assert saved_request.preview_url == f"https://preview.local/projects/{project.id}"
    finally:
        db.close()


def test_deploy_approval_moves_project_to_deploy_approved(tmp_path: Path):
    db = _make_db_session(tmp_path)
    try:
        client = _make_user(db, "client+deploy2@example.com", "client")
        admin = _make_user(db, "admin+deploy2@example.com", "owner")
        project = _make_project(db, client.id, ProjectState.BUILD_GENERATED.value)

        submit_project_deploy_for_approval(project_id=project.id, user=admin, db=db)
        approved = approve_project_deploy(project_id=project.id, user=admin, db=db)

        assert approved.state == ProjectState.DEPLOY_APPROVED.value
        assert approved.deploy_status == "deploy_approved"
        assert approved.preview_url == f"https://preview.local/projects/{project.id}"

        db.refresh(project)
        assert project.state == ProjectState.DEPLOY_APPROVED.value

        saved_request = (
            db.query(ProjectDeployRequest)
            .filter(ProjectDeployRequest.project_id == project.id)
            .first()
        )
        assert saved_request is not None
        assert saved_request.status == "deploy_approved"
        assert saved_request.approved_at is not None
    finally:
        db.close()


def test_deploy_reject_returns_project_to_build_generated(tmp_path: Path):
    db = _make_db_session(tmp_path)
    try:
        client = _make_user(db, "client+deploy3@example.com", "client")
        admin = _make_user(db, "admin+deploy3@example.com", "admin")
        project = _make_project(db, client.id, ProjectState.BUILD_GENERATED.value)

        submit_project_deploy_for_approval(project_id=project.id, user=admin, db=db)
        rejected = reject_project_deploy(project_id=project.id, user=admin, db=db)

        assert rejected.state == ProjectState.BUILD_GENERATED.value
        assert rejected.deploy_status == "preview_ready"

        db.refresh(project)
        assert project.state == ProjectState.BUILD_GENERATED.value
    finally:
        db.close()
