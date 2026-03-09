from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..ai.design_brief import generate_design_brief_for_project
from ..deps import current_user, get_db
from ..models import Project, ProjectDesignBrief, User
from ..project_state import ProjectState, ensure_transition
from ..schemas import AdminDesignDecisionOut, DesignBriefGenerateOut

router = APIRouter(prefix="/admin", tags=["admin"])


def _require_design_approver(user: User) -> None:
    if user.role not in {"owner", "admin"}:
        raise HTTPException(status_code=403, detail="Admin access required")


@router.post("/projects/{project_id}/design/generate", response_model=DesignBriefGenerateOut)
def generate_project_design_brief(
    project_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    _require_design_approver(user)

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        design_brief = generate_design_brief_for_project(db=db, project=project)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return DesignBriefGenerateOut(
        project_id=project.id,
        state=project.state,
        brief_id=design_brief.id,
        brief_text=design_brief.brief_text,
    )


@router.post("/projects/{project_id}/design/submit", response_model=AdminDesignDecisionOut)
def submit_project_design_for_approval(
    project_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    _require_design_approver(user)

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    design_brief = db.query(ProjectDesignBrief).filter(ProjectDesignBrief.project_id == project.id).first()
    if not design_brief:
        raise HTTPException(status_code=409, detail="Design brief not generated")

    current_state = ProjectState(project.state)
    if current_state != ProjectState.DESIGN_GENERATED:
        raise HTTPException(status_code=409, detail="Project is not in design_generated state")

    project.state = ensure_transition(current_state, ProjectState.AWAITING_ADMIN_DESIGN_APPROVAL).value
    db.add(project)
    db.commit()
    db.refresh(project)

    return AdminDesignDecisionOut(project_id=project.id, state=project.state)


@router.post("/projects/{project_id}/design/approve", response_model=AdminDesignDecisionOut)
def approve_project_design(
    project_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    _require_design_approver(user)

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    current_state = ProjectState(project.state)
    if current_state != ProjectState.AWAITING_ADMIN_DESIGN_APPROVAL:
        raise HTTPException(status_code=409, detail="Project is not awaiting admin design approval")

    project.state = ensure_transition(current_state, ProjectState.DESIGN_APPROVED).value
    db.add(project)
    db.commit()
    db.refresh(project)

    return AdminDesignDecisionOut(project_id=project.id, state=project.state)


@router.post("/projects/{project_id}/design/reject", response_model=AdminDesignDecisionOut)
def reject_project_design(
    project_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    _require_design_approver(user)

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    current_state = ProjectState(project.state)
    if current_state != ProjectState.AWAITING_ADMIN_DESIGN_APPROVAL:
        raise HTTPException(status_code=409, detail="Project is not awaiting admin design approval")

    project.state = ensure_transition(current_state, ProjectState.DESIGN_GENERATED).value
    db.add(project)
    db.commit()
    db.refresh(project)

    return AdminDesignDecisionOut(project_id=project.id, state=project.state)
