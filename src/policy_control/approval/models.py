
"""
Approval Engine Data Models
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from ..common.constants import ApprovalStatus, RequestType, TimeoutAction


@dataclass
class ApprovalRequest:
    """审批请求模型"""

    id: UUID = field(default_factory=uuid4)
    thread_id: UUID = field(default_factory=uuid4)
    action_run_id: UUID | None = None
    request_type: RequestType = RequestType.MESSAGE_SEND
    reason_code: str = ""
    reason_description: str | None = None
    requester_principal_id: UUID = field(default_factory=uuid4)
    approver_principal_id: UUID | None = None
    status: ApprovalStatus = ApprovalStatus.PENDING
    preview: dict[str, Any] | None = None
    resolution: dict[str, Any] | None = None
    resolved_at: datetime | None = None
    resolved_by: UUID | None = None
    timeout_at: datetime | None = None
    timeout_action: TimeoutAction = TimeoutAction.ESCALATE
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def is_resolved(self) -> bool:
        """检查是否已解决"""
        return self.status not in [ApprovalStatus.PENDING]

    def is_pending(self) -> bool:
        """检查是否待审批"""
        return self.status == ApprovalStatus.PENDING

    def is_timed_out(self) -> bool:
        """检查是否超时"""
        if not self.timeout_at:
            return False
        return datetime.utcnow() > self.timeout_at


@dataclass
class ApprovalResolution:
    """审批决议"""

    action: str  # APPROVE, REJECT, MODIFY, TAKEOVER
    modified_content: str | None = None
    reason: str | None = None
    resolved_by: UUID = field(default_factory=uuid4)
