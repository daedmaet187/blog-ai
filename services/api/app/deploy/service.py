from datetime import datetime

from sqlalchemy.orm import Session

from ..models import Project, ProjectDeployRequest


class DeployService:
    """Deterministic deploy preview service for Task 7.

    No real cloud calls are made. Preview URLs are generated from the project id.
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
