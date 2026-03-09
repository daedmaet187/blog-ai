from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..deps import current_user, get_db
from ..models import Project, User
from ..payments.wayl_client import WaylClient
from ..project_state import ProjectState, ensure_transition
from ..schemas import DepositSessionCreate, DepositSessionOut

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/deposits/session", response_model=DepositSessionOut)
def create_deposit_session(
    payload: DepositSessionCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    project = (
        db.query(Project)
        .filter(Project.id == payload.project_id, Project.client_user_id == user.id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    current_state = ProjectState(project.state)
    if current_state == ProjectState.SUBMITTED:
        project.state = ensure_transition(current_state, ProjectState.DEPOSIT_PENDING).value
        db.add(project)
        db.commit()
        db.refresh(project)
    elif current_state != ProjectState.DEPOSIT_PENDING:
        raise HTTPException(status_code=409, detail="Project is not eligible for deposit")

    session = WaylClient().create_deposit_session(
        project_id=project.id,
        title=project.title,
        package=project.package,
    )

    return DepositSessionOut(
        project_id=project.id,
        state=project.state,
        session_id=str(session.get("session_id", "")),
        checkout_url=str(session.get("checkout_url", "")),
    )


@router.post("/wayl/webhook")
async def wayl_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    signature = request.headers.get("X-Wayl-Signature", "")
    client = WaylClient()

    if not client.verify_webhook_signature(payload, signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    event = client.decode_event(payload)
    if event.get("status") != "success":
        return {"ok": True}

    metadata = event.get("metadata", {})
    project_id = metadata.get("project_id") or event.get("project_id")
    if not project_id:
        return {"ok": True}

    project = db.query(Project).filter(Project.id == int(project_id)).first()
    if not project:
        return {"ok": True}

    current_state = ProjectState(project.state)
    if current_state == ProjectState.DEPOSIT_PENDING:
        project.state = ensure_transition(current_state, ProjectState.DEPOSIT_PAID).value
        db.add(project)
        db.commit()

    return {"ok": True}
