from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..deps import current_user, get_db
from ..models import Project, User
from ..schemas import ProjectRequestCreate, ProjectRequestOut

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
