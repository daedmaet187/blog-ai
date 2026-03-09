from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..ai.clarification import generate_clarification_questions, is_clarification_complete
from ..deps import current_user, get_db
from ..models import Project, ProjectClarification, User
from ..project_state import ProjectState, ensure_transition
from ..schemas import (
    ClarificationAnswersSubmitIn,
    ClarificationAnswersSubmitOut,
    ClarificationQuestionOut,
    ClarificationStartOut,
    ProjectRequestCreate,
    ProjectRequestOut,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/requests", response_model=ProjectRequestOut)
def create_project_request(
    payload: ProjectRequestCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    project = Project(
        client_user_id=user.id,
        title=payload.title,
        package=payload.package,
        brief_en=payload.brief_en,
        brief_ar=payload.brief_ar,
        state="submitted",
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/requests", response_model=list[ProjectRequestOut])
def list_my_project_requests(
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Project)
        .filter(Project.client_user_id == user.id)
        .order_by(Project.id.desc())
        .all()
    )


@router.post("/{project_id}/clarification/start", response_model=ClarificationStartOut)
def start_project_clarification(
    project_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.client_user_id == user.id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    current_state = ProjectState(project.state)
    if current_state not in {ProjectState.DEPOSIT_PAID, ProjectState.CLARIFICATION_NEEDED}:
        raise HTTPException(status_code=409, detail="Project is not eligible for clarification")

    existing_questions = (
        db.query(ProjectClarification)
        .filter(ProjectClarification.project_id == project.id)
        .order_by(ProjectClarification.id.asc())
        .all()
    )

    if not existing_questions:
        generated_questions = generate_clarification_questions(
            title=project.title,
            brief_en=project.brief_en,
            brief_ar=project.brief_ar,
        )
        for question in generated_questions:
            db.add(
                ProjectClarification(
                    project_id=project.id,
                    question_key=question["key"],
                    question_text=question["question"],
                )
            )
        db.commit()

    questions = (
        db.query(ProjectClarification)
        .filter(ProjectClarification.project_id == project.id)
        .order_by(ProjectClarification.id.asc())
        .all()
    )

    if not questions:
        project.state = ensure_transition(current_state, ProjectState.READY_FOR_DESIGN).value
        db.add(project)
        db.commit()
        db.refresh(project)
        return ClarificationStartOut(project_id=project.id, state=project.state, questions=[])

    if current_state == ProjectState.DEPOSIT_PAID:
        project.state = ensure_transition(current_state, ProjectState.CLARIFICATION_NEEDED).value
        db.add(project)
        db.commit()
        db.refresh(project)

    return ClarificationStartOut(
        project_id=project.id,
        state=project.state,
        questions=[ClarificationQuestionOut.model_validate(question) for question in questions],
    )


@router.post("/{project_id}/clarification/answers", response_model=ClarificationAnswersSubmitOut)
def submit_clarification_answers(
    project_id: int,
    payload: ClarificationAnswersSubmitIn,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.client_user_id == user.id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if ProjectState(project.state) != ProjectState.CLARIFICATION_NEEDED:
        raise HTTPException(status_code=409, detail="Project is not awaiting clarification")

    for item in payload.answers:
        clarification = (
            db.query(ProjectClarification)
            .filter(
                ProjectClarification.id == item.question_id,
                ProjectClarification.project_id == project.id,
            )
            .first()
        )
        if clarification:
            clarification.answer_text = item.answer_text.strip()
            db.add(clarification)

    db.commit()

    questions = (
        db.query(ProjectClarification)
        .filter(ProjectClarification.project_id == project.id)
        .order_by(ProjectClarification.id.asc())
        .all()
    )

    pending_questions = [q for q in questions if not (q.answer_text or "").strip()]
    answered_keys = {q.question_key for q in questions if (q.answer_text or "").strip()}

    if not pending_questions and is_clarification_complete(answered_keys):
        project.state = ensure_transition(
            ProjectState(project.state), ProjectState.READY_FOR_DESIGN
        ).value
        db.add(project)
        db.commit()

    db.refresh(project)

    return ClarificationAnswersSubmitOut(
        project_id=project.id,
        state=project.state,
        pending_questions=[ClarificationQuestionOut.model_validate(q) for q in pending_questions],
    )
