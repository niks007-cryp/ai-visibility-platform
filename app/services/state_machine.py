from typing import Dict, Set
from app.models.analysis_job import AnalysisJobStatus


class InvalidStateTransitionException(Exception):
    """Exception raised when an illegal job state transition is attempted."""
    def __init__(self, current_status: AnalysisJobStatus, target_status: AnalysisJobStatus):
        self.current_status = current_status
        self.target_status = target_status
        curr_val = current_status.value if hasattr(current_status, 'value') else current_status
        targ_val = target_status.value if hasattr(target_status, 'value') else target_status
        super().__init__(
            f"Cannot transition job status from '{curr_val}' to '{targ_val}'."
        )


class JobStateMachine:
    """Dedicated State Machine validating Analysis Job status transitions."""

    # Allowed transitions map: current_status -> set of valid target_statuses
    ALLOWED_TRANSITIONS: Dict[AnalysisJobStatus, Set[AnalysisJobStatus]] = {
        AnalysisJobStatus.PENDING: {
            AnalysisJobStatus.RUNNING,
            AnalysisJobStatus.CANCELLED
        },
        AnalysisJobStatus.RUNNING: {
            AnalysisJobStatus.COMPLETED,
            AnalysisJobStatus.FAILED,
            AnalysisJobStatus.CANCELLED
        },
        AnalysisJobStatus.COMPLETED: set(),  # Terminal state
        AnalysisJobStatus.FAILED: set(),     # Terminal state
        AnalysisJobStatus.CANCELLED: set(),  # Terminal state
    }

    @classmethod
    def validate_transition(
        cls,
        current_status: AnalysisJobStatus,
        target_status: AnalysisJobStatus
    ) -> None:
        """Validates if transitioning from current_status to target_status is allowed.
        
        Raises InvalidStateTransitionException if transition is prohibited.
        """
        if current_status == target_status:
            return  # No-op same state transition

        allowed_targets = cls.ALLOWED_TRANSITIONS.get(current_status, set())
        if target_status not in allowed_targets:
            raise InvalidStateTransitionException(
                current_status=current_status,
                target_status=target_status
            )


state_machine = JobStateMachine()
