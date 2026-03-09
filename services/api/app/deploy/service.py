from datetime import datetime

from sqlalchemy.orm import Session

from ..models import Project, ProjectDeployRequest
from ..project_state import ProjectState


class DeployService:
    """Deterministic deploy preview/domain mapping service.

    No real cloud calls are made. URLs are generated from the project id.
    """

    def generate_preview(self, *, db: Session, project: Project) -> ProjectDeployRequest:
        preview_url = f"https://preview.local/projects/{project.id}"
        record = db.query(ProjectDeployRequest).filter(ProjectDeployRequest.project_id == project.id).first()

        if record:
            record.preview_url = preview_url
            record.status = "preview_ready"
            record.submitted_at = datetime.utcnow()
        else:
            record = ProjectDeployRequest(
                project_id=project.id,
                preview_url=preview_url,
                status="preview_ready",
                submitted_at=datetime.utcnow(),
            )

        db.add(record)
        return record

    def map_domain(self, *, project: Project, deploy_request: ProjectDeployRequest) -> str:
        if ProjectState(project.state) != ProjectState.DELIVERED:
            raise ValueError("Final payment is required before domain mapping")

        domain = f"project-{project.id}.launch.local"
        deploy_request.status = "domain_mapped"
        return domain
