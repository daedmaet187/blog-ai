from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth import hash_password
from app.db import Base
from app.models import Project, User
from app.project_state import ProjectState
from app.routers.projects import start_project_clarification, submit_clarification_answers
from app.schemas import ClarificationAnswersSubmitIn


def _make_db_session(tmp_path: Path) -> Session:
    db_file = tmp_path / "test_clarification_loop.db"
    engine = create_engine(
        f"sqlite:///{db_file}", connect_args={"check_same_thread": False}, future=True
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


def _make_user(db: Session, email: str = "client@example.com") -> User:
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


def _make_project(db: Session, user_id: int, state: str, brief_en: str) -> Project:
    project = Project(
        client_user_id=user_id,
        title="Simple Landing",
        package="starter",
        brief_en=brief_en,
        brief_ar="هذه صفحة هبوط للشركة.",
        state=state,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def test_unclear_request_enters_clarification_loop_then_ready_for_design(tmp_path: Path):
    db = _make_db_session(tmp_path)
    try:
        user = _make_user(db)
        project = _make_project(
            db,
            user.id,
            state=ProjectState.DEPOSIT_PAID.value,
            brief_en="I need a page for my business.",
        )

        started = start_project_clarification(project_id=project.id, user=user, db=db)

        assert started.project_id == project.id
        assert started.state == ProjectState.CLARIFICATION_NEEDED.value
        assert len(started.questions) >= 1

        answers = ClarificationAnswersSubmitIn(
            answers=[
                {"question_id": question.id, "answer_text": f"answer for {question.question_key}"}
                for question in started.questions
            ]
        )
        submitted = submit_clarification_answers(project_id=project.id, payload=answers, user=user, db=db)

        assert submitted.state == ProjectState.READY_FOR_DESIGN.value
        assert submitted.pending_questions == []

        db.refresh(project)
        assert project.state == ProjectState.READY_FOR_DESIGN.value
    finally:
        db.close()
