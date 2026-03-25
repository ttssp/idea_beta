
"""
Approval Engine Data Models
"""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from uuid import UUID, uuid4
from datetime import datetime, timedelta

from ..common.constants import ApprovalStatus, RequestType, TimeoutAction


@dataclass
class ApprovalRequest:
    """审批请求模型"""

    id: UUID = field(default_factory=uuid4)
    thread_id: UUID = field(default_factory=uuid4)
    action_run_id: Optional[UUID] = None
    request_type: RequestType = RequestType.MESSAGE_SEND
    reason_code: str = ""
    reason_description: Optional[str] = None
    requester_principal_id: UUID = field(default_factory=uuid4)
    approver_principal_id: Optional[UUID] = None
    status: ApprovalStatus = ApprovalStatus.PENDING
    preview: Optional[Dict[str, Any]] = None
    resolution: Optional[Dict[str, Any]] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[UUID] = None
    timeout_at: Optional[datetime] = None
    timeout_action: TimeoutAction = TimeoutAction.ESCALATE
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def is_resolved(self) -&gt; bool:
        """检查是否已解决"""
        return self.status not in [ApprovalStatus.PENDING]

    def is_pending(self) -&gt; bool:
        """检查是否待审批"""
        return self.status == ApprovalStatus.PENDING

    def is_timed_out(self) -&gt; bool:
        """检查是否超时"""
        if not self.timeout_at:
            return False
        return datetime.utcnow() &gt; self.timeout_at


@dataclass
class ApprovalResolution:
    """审批决议"""

    action: str  # APPROVE, REJECT, MODIFY, TAKEOVER
    modified_content: Optional[str] = None
    reason: Optional[str] = None
    resolved_by: UUID = field(default_factory=uuid4)
