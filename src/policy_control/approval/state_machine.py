
"""
Approval State Machine

审批状态机
"""
from typing import List, Set

from ..common.constants import ApprovalStatus
from ..common.exceptions import ApprovalStateTransitionError


class ApprovalStateMachine:
    """
    审批状态机

    状态流转:
        PENDING -> APPROVED
        PENDING -> REJECTED
        PENDING -> MODIFIED
        PENDING -> TAKEN_OVER
        PENDING -> CANCELLED
        PENDING -> TIMEOUT
    """

    # 允许的状态流转
    ALLOWED_TRANSITIONS = {
        ApprovalStatus.PENDING: {
            ApprovalStatus.APPROVED,
            ApprovalStatus.REJECTED,
            ApprovalStatus.MODIFIED,
            ApprovalStatus.TAKEN_OVER,
            ApprovalStatus.CANCELLED,
            ApprovalStatus.TIMEOUT,
        },
        # 终态不允许再变更
        ApprovalStatus.APPROVED: set(),
        ApprovalStatus.REJECTED: set(),
        ApprovalStatus.MODIFIED: set(),
        ApprovalStatus.TAKEN_OVER: set(),
        ApprovalStatus.CANCELLED: set(),
        ApprovalStatus.TIMEOUT: set(),
    }

    @classmethod
    def can_transition(cls, from_status: ApprovalStatus, to_status: ApprovalStatus) -> bool:
        """检查是否允许状态流转"""
        allowed = cls.ALLOWED_TRANSITIONS.get(from_status, set())
        return to_status in allowed

    @classmethod
    def transition(cls, current_status: ApprovalStatus, target_status: ApprovalStatus) -> ApprovalStatus:
        """
        执行状态流转

        Raises:
            ApprovalStateTransitionError: 如果状态流转不允许
        """
        if not cls.can_transition(current_status, target_status):
            raise ApprovalStateTransitionError(
                f"Cannot transition from {current_status.value} to {target_status.value}"
            )
        return target_status

    @classmethod
    def is_terminal(cls, status: ApprovalStatus) -> bool:
        """检查是否是终态"""
        return len(cls.ALLOWED_TRANSITIONS.get(status, set())) == 0

    @classmethod
    def get_allowed_next_statuses(cls, status: ApprovalStatus) -> Set[ApprovalStatus]:
        """获取允许的下一状态"""
        return cls.ALLOWED_TRANSITIONS.get(status, set()).copy()
