from sqlalchemy.orm import Session

from ..models import Project, ProjectClarification, ProjectDesignBrief
from ..project_state import ProjectState, ensure_transition


def generate_design_brief_content(*, title: str, package: str, brief_en: str, brief_ar: str, answers: list[str]) -> str:
    lines = [
        f"Project: {title}",
        f"Package: {package}",
        f"English brief: {brief_en.strip()}",
        f"Arabic brief: {brief_ar.strip()}",
    ]

    if answers:
        lines.append("Clarifications:")
        for answer in answers:
            lines.append(f"- {answer}")

    lines.append("Design constraints: keep structure conversion-focused and mobile-first.")
    return "\n".join(lines)


def generate_design_brief_for_project(*, db: Session, project: Project) -> ProjectDesignBrief:
    current_state = ProjectState(project.state)
    if current_state != ProjectState.READY_FOR_DESIGN:
        raise ValueError("Project is not ready for design generation")

    clarifications = (
        db.query(ProjectClarification)
        .filter(ProjectClarification.project_id == project.id)
        .order_by(ProjectClarification.id.asc())
        .all()
    )
    answers = [c.answer_text.strip() for c in clarifications if (c.answer_text or "").strip()]

    brief_content = generate_design_brief_content(
        title=project.title,
        package=project.package,
        brief_en=project.brief_en,
        brief_ar=project.brief_ar,
        answers=answers,
    )

    existing = (
        db.query(ProjectDesignBrief)
        .filter(ProjectDesignBrief.project_id == project.id)
        .first()
    )
    if existing:
        existing.brief_text = brief_content
        design_brief = existing
    else:
        design_brief = ProjectDesignBrief(project_id=project.id, brief_text=brief_content)

    project.state = ensure_transition(current_state, ProjectState.DESIGN_GENERATED).value

    db.add(design_brief)
    db.add(project)
    db.commit()
    db.refresh(design_brief)
    db.refresh(project)
    return design_brief
