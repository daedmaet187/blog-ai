import pytest

from app.project_state import ProjectState, InvalidProjectTransitionError, can_transition, ensure_transition


@pytest.mark.parametrize(
    "current_state,next_state",
    [
        (ProjectState.SUBMITTED, ProjectState.DEPOSIT_PENDING),
        (ProjectState.DEPOSIT_PENDING, ProjectState.DEPOSIT_PAID),
        (ProjectState.DEPOSIT_PAID, ProjectState.CLARIFICATION_NEEDED),
        (ProjectState.DEPOSIT_PAID, ProjectState.READY_FOR_DESIGN),
        (ProjectState.CLARIFICATION_NEEDED, ProjectState.READY_FOR_DESIGN),
        (ProjectState.READY_FOR_DESIGN, ProjectState.DESIGN_GENERATED),
        (ProjectState.DESIGN_GENERATED, ProjectState.AWAITING_ADMIN_DESIGN_APPROVAL),
        (ProjectState.AWAITING_ADMIN_DESIGN_APPROVAL, ProjectState.DESIGN_APPROVED),
        (ProjectState.DESIGN_APPROVED, ProjectState.BUILD_GENERATED),
        (ProjectState.BUILD_GENERATED, ProjectState.AWAITING_ADMIN_DEPLOY_APPROVAL),
        (ProjectState.AWAITING_ADMIN_DEPLOY_APPROVAL, ProjectState.DEPLOY_APPROVED),
        (ProjectState.DEPLOY_APPROVED, ProjectState.DELIVERED),
    ],
)
def test_valid_project_state_transitions(current_state: ProjectState, next_state: ProjectState) -> None:
    assert can_transition(current_state, next_state) is True
    assert ensure_transition(current_state, next_state) == next_state


@pytest.mark.parametrize(
    "current_state,next_state",
    [
        (ProjectState.SUBMITTED, ProjectState.DEPOSIT_PAID),
        (ProjectState.DEPOSIT_PENDING, ProjectState.READY_FOR_DESIGN),
        (ProjectState.READY_FOR_DESIGN, ProjectState.DELIVERED),
        (ProjectState.DELIVERED, ProjectState.SUBMITTED),
    ],
)
def test_invalid_project_state_transitions(current_state: ProjectState, next_state: ProjectState) -> None:
    assert can_transition(current_state, next_state) is False
    with pytest.raises(InvalidProjectTransitionError):
        ensure_transition(current_state, next_state)
