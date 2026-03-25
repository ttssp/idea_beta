
"""
Approval API

审批管理API
"""
from dataclasses import dataclass
from uuid import UUID

from ..approval.models import ApprovalRequest, ApprovalResolution
from ..approval.service import ApprovalService
from ..common.constants import ApprovalStatus


@dataclass
class ResolveApprovalRequest:
    action: str  # APPROVE, REJECT, MODIFY, TAKEOVER
    modified_content: str | None = None
    reason: str | None = None


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
        thread_id: UUID | None = None,
        status: ApprovalStatus | None = None,
        approver_principal_id: UUID | None = None,
        limit: int = 100,
    ) -> list[ApprovalRequest]:
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

    def get_approval(self, approval_id: UUID) -> ApprovalRequest | None:
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
