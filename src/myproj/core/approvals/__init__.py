"""
Approvals - Communication OS

The future home for approval logic previously in policy_control/approval.
This package handles:
- Approval requests
- Approval state machine
- Approval resolution
- Sender stack in approval previews
"""

from myproj.core.approvals.interfaces import ApprovalService
from myproj.core.approvals.types import (
    ApprovalRequest,
    ApprovalResolution,
    ApprovalStatus,
    ApprovalAction,
)

__all__ = [
    "ApprovalService",
    "ApprovalRequest",
    "ApprovalResolution",
    "ApprovalStatus",
    "ApprovalAction",
]
