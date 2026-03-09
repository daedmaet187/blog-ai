from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..ai.design_brief import generate_design_brief_for_project
from ..codegen.template_engine import generate_template
from ..deploy.service import DeployService
from ..deps import current_user, get_db
from ..models import Project, ProjectDeployRequest, ProjectDesignBrief, ProjectRepository, User
from ..project_state import ProjectState, ensure_transition
from ..repos.github_provisioner import GitHubProvisioner
from ..schemas import (
    AdminDeployDecisionOut,
    AdminDesignDecisionOut,
    BuildGenerateOut,
    DeploySubmitOut,
    DesignBriefGenerateOut,
)

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


@router.post("/projects/{project_id}/build/generate", response_model=BuildGenerateOut)
def generate_project_build(
    project_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    _require_design_approver(user)

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    current_state = ProjectState(project.state)
    if current_state != ProjectState.DESIGN_APPROVED:
        raise HTTPException(status_code=409, detail="Project is not approved for build generation")

    repo = GitHubProvisioner().provision_for_project(
        client_user_id=project.client_user_id,
        project_id=project.id,
        title=project.title,
    )
    generated = generate_template(
        package=project.package,
        title=project.title,
        brief_en=project.brief_en,
        brief_ar=project.brief_ar,
    )
    generated_paths = sorted(generated.files.keys())

    existing = db.query(ProjectRepository).filter(ProjectRepository.project_id == project.id).first()
    if existing:
        existing.repo_full_name = repo.full_name
        existing.repo_url = repo.html_url
        existing.clone_url = repo.clone_url
        existing.default_branch = repo.default_branch
        existing.generated_files = "\n".join(generated_paths)
        record = existing
    else:
        record = ProjectRepository(
            project_id=project.id,
            repo_full_name=repo.full_name,
            repo_url=repo.html_url,
            clone_url=repo.clone_url,
            default_branch=repo.default_branch,
            generated_files="\n".join(generated_paths),
        )

    project.state = ensure_transition(current_state, ProjectState.BUILD_GENERATED).value

    db.add(record)
    db.add(project)
    db.commit()
    db.refresh(project)

    return BuildGenerateOut(
        project_id=project.id,
        state=project.state,
        repo_full_name=repo.full_name,
        repo_url=repo.html_url,
        generated_files=generated_paths,
    )


@router.post("/projects/{project_id}/deploy/submit", response_model=DeploySubmitOut)
def submit_project_deploy_for_approval(
    project_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    _require_design_approver(user)

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    current_state = ProjectState(project.state)
    if current_state != ProjectState.BUILD_GENERATED:
        raise HTTPException(status_code=409, detail="Project is not ready for deploy submission")

    deploy_request = DeployService().generate_preview(db=db, project=project)
    deploy_request.status = "awaiting_admin_deploy_approval"
    project.state = ensure_transition(current_state, ProjectState.AWAITING_ADMIN_DEPLOY_APPROVAL).value

    db.add(deploy_request)
    db.add(project)
    db.commit()
    db.refresh(project)
    db.refresh(deploy_request)

    return DeploySubmitOut(
        project_id=project.id,
        state=project.state,
        deploy_status=deploy_request.status,
        preview_url=deploy_request.preview_url,
    )


@router.post("/projects/{project_id}/deploy/approve", response_model=AdminDeployDecisionOut)
def approve_project_deploy(
    project_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    _require_design_approver(user)

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    deploy_request = db.query(ProjectDeployRequest).filter(ProjectDeployRequest.project_id == project.id).first()
    if not deploy_request:
        raise HTTPException(status_code=409, detail="Deploy request not found")

    current_state = ProjectState(project.state)
    if current_state != ProjectState.AWAITING_ADMIN_DEPLOY_APPROVAL:
        raise HTTPException(status_code=409, detail="Project is not awaiting admin deploy approval")

    deploy_request.status = "deploy_approved"
    deploy_request.approved_at = datetime.utcnow()
    project.state = ensure_transition(current_state, ProjectState.DEPLOY_APPROVED).value

    db.add(deploy_request)
    db.add(project)
    db.commit()
    db.refresh(project)
    db.refresh(deploy_request)

    return AdminDeployDecisionOut(
        project_id=project.id,
        state=project.state,
        deploy_status=deploy_request.status,
        preview_url=deploy_request.preview_url,
    )


@router.post("/projects/{project_id}/deploy/reject", response_model=AdminDeployDecisionOut)
def reject_project_deploy(
    project_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    _require_design_approver(user)

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    deploy_request = db.query(ProjectDeployRequest).filter(ProjectDeployRequest.project_id == project.id).first()
    if not deploy_request:
        raise HTTPException(status_code=409, detail="Deploy request not found")

    current_state = ProjectState(project.state)
    if current_state != ProjectState.AWAITING_ADMIN_DEPLOY_APPROVAL:
        raise HTTPException(status_code=409, detail="Project is not awaiting admin deploy approval")

    deploy_request.status = "preview_ready"
    project.state = ProjectState.BUILD_GENERATED.value

    db.add(deploy_request)
    db.add(project)
    db.commit()
    db.refresh(project)
    db.refresh(deploy_request)

    return AdminDeployDecisionOut(
        project_id=project.id,
        state=project.state,
        deploy_status=deploy_request.status,
        preview_url=deploy_request.preview_url,
    )
