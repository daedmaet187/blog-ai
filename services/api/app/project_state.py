from enum import StrEnum


class ProjectState(StrEnum):
    SUBMITTED = "submitted"
    DEPOSIT_PENDING = "deposit_pending"
    DEPOSIT_PAID = "deposit_paid"
    CLARIFICATION_NEEDED = "clarification_needed"
    READY_FOR_DESIGN = "ready_for_design"
    DESIGN_GENERATED = "design_generated"
    AWAITING_ADMIN_DESIGN_APPROVAL = "awaiting_admin_design_approval"
    DESIGN_APPROVED = "design_approved"
    BUILD_GENERATED = "build_generated"
    AWAITING_ADMIN_DEPLOY_APPROVAL = "awaiting_admin_deploy_approval"
    DEPLOY_APPROVED = "deploy_approved"
    DELIVERED = "delivered"


_ALLOWED_TRANSITIONS: dict[ProjectState, set[ProjectState]] = {
    ProjectState.SUBMITTED: {ProjectState.DEPOSIT_PENDING},
    ProjectState.DEPOSIT_PENDING: {ProjectState.DEPOSIT_PAID},
    ProjectState.DEPOSIT_PAID: {ProjectState.CLARIFICATION_NEEDED, ProjectState.READY_FOR_DESIGN},
    ProjectState.CLARIFICATION_NEEDED: {ProjectState.READY_FOR_DESIGN},
    ProjectState.READY_FOR_DESIGN: {ProjectState.DESIGN_GENERATED},
    ProjectState.DESIGN_GENERATED: {ProjectState.AWAITING_ADMIN_DESIGN_APPROVAL},
    ProjectState.AWAITING_ADMIN_DESIGN_APPROVAL: {ProjectState.DESIGN_APPROVED},
    ProjectState.DESIGN_APPROVED: {ProjectState.BUILD_GENERATED},
    ProjectState.BUILD_GENERATED: {ProjectState.AWAITING_ADMIN_DEPLOY_APPROVAL},
    ProjectState.AWAITING_ADMIN_DEPLOY_APPROVAL: {ProjectState.DEPLOY_APPROVED},
    ProjectState.DEPLOY_APPROVED: {ProjectState.DELIVERED},
    ProjectState.DELIVERED: set(),
}


class InvalidProjectTransitionError(ValueError):
    pass


def can_transition(current_state: ProjectState, next_state: ProjectState) -> bool:
    return next_state in _ALLOWED_TRANSITIONS.get(current_state, set())


def ensure_transition(current_state: ProjectState, next_state: ProjectState) -> ProjectState:
    if not can_transition(current_state, next_state):
        raise InvalidProjectTransitionError(
            f"Invalid project state transition: {current_state.value} -> {next_state.value}"
        )
    return next_state
