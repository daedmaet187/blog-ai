from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth import hash_password
from app.db import Base
from app.models import Project, ProjectRepository, User
from app.project_state import ProjectState
from app.routers.admin import generate_project_build


def _make_db_session(tmp_path: Path) -> Session:
    db_file = tmp_path / "test_repo_codegen_flow.db"
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


def _make_project(db: Session, user_id: int, package: str = "growth") -> Project:
    project = Project(
        client_user_id=user_id,
        title="Growth Launch",
        package=package,
        brief_en="Create a multilingual SaaS landing page for trial signups.",
        brief_ar="أنشئ صفحة هبوط متعددة اللغات لخدمة SaaS لزيادة التسجيل التجريبي.",
        state=ProjectState.DESIGN_APPROVED.value,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def test_build_generation_persists_repo_metadata_and_package_templates(monkeypatch, tmp_path: Path):
    db = _make_db_session(tmp_path)
    try:
        client = _make_user(db, "client+repo@example.com", "client")
        admin = _make_user(db, "admin+repo@example.com", "admin")
        project = _make_project(db, client.id, package="growth")

        def _fake_create_repository(self, *, repo_name: str, description: str):
            assert f"p{project.id}" in repo_name
            assert "growth-launch" in repo_name
            assert "Growth Launch" in description
            return {
                "full_name": f"sandbox/{repo_name}",
                "html_url": f"https://github.com/sandbox/{repo_name}",
                "clone_url": f"https://github.com/sandbox/{repo_name}.git",
                "default_branch": "main",
            }

        monkeypatch.setattr(
            "app.repos.github_provisioner.GitHubProvisioner.create_repository",
            _fake_create_repository,
        )

        out = generate_project_build(project_id=project.id, user=admin, db=db)

        assert out.project_id == project.id
        assert out.state == ProjectState.BUILD_GENERATED.value
        assert out.repo_full_name.startswith("sandbox/")
        assert "src/sections/social-proof.tsx" in out.generated_files
        assert "src/sections/pricing.tsx" not in out.generated_files

        db.refresh(project)
        assert project.state == ProjectState.BUILD_GENERATED.value

        saved_repo = db.query(ProjectRepository).filter(ProjectRepository.project_id == project.id).first()
        assert saved_repo is not None
        assert saved_repo.repo_full_name == out.repo_full_name
        assert saved_repo.repo_url == out.repo_url
        assert "src/sections/social-proof.tsx" in saved_repo.generated_files.splitlines()
    finally:
        db.close()
