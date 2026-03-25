
"""
Approval API

审批管理API
"""
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from uuid import UUID

from ..common.constants import ApprovalStatus, RequestType, TimeoutAction
from ..approval.models import ApprovalRequest, ApprovalResolution
from ..approval.service import ApprovalService


@dataclass
class ResolveApprovalRequest:
    action: str  # APPROVE, REJECT, MODIFY, TAKEOVER
    modified_content: Optional[str] = None
    reason: Optional[str] = None


class ApprovalAPI:
    """
    Approval API

    Endpoints:
        GET /approvals
        GET /approvals/{id}
        POST /approvals/{id}:resolve
    """

    def __init__(self, approval_service: ApprovalService):
        self.service = approval_service

    def get_approvals(
        self,
        thread_id: Optional[UUID] = None,
        status: Optional[ApprovalStatus] = None,
        approver_principal_id: Optional[UUID] = None,
        limit: int = 100,
    ) -> List[ApprovalRequest]:
        """
        GET /approvals

        查询待审批列表
        """
        return self.service.list_requests(
            thread_id=thread_id,
            status=status,
            approver_principal_id=approver_principal_id,
            limit=limit,
        )

    def get_approval(self, approval_id: UUID) -> Optional[ApprovalRequest]:
        """
        GET /approvals/{id}

        查询审批详情
        """
        return self.service.get_request(approval_id)

    def resolve_approval(
        self,
        approval_id: UUID,
        request: ResolveApprovalRequest,
        resolved_by: UUID,
    ) -> ApprovalRequest:
        """
        POST /approvals/{id}:resolve

        审批操作（approve/reject/modify/takeover）
        """
        resolution = ApprovalResolution(
            action=request.action,
            modified_content=request.modified_content,
            reason=request.reason,
            resolved_by=resolved_by,
        )
        return self.service.resolve(approval_id, resolution)
